import json

from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseForbidden,
    HttpResponseNotFound,
)

from dcapp.helpers import (
    create_discount_codes_with_retry_for_uniqueness,
    reserve_discount_code_retry_race_condition,
)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateDiscountCode(View):
    def post(self, request):
        if not self._is_request_valid(request):
            return HttpResponseBadRequest()

        body = json.loads(request.body)
        created = create_discount_codes_with_retry_for_uniqueness(
            percent=body['percent'],
            brand_slug=body['brand_slug'],
            count=body['count']
        )
        if not created:
            return HttpResponseServerError()

        return HttpResponse()

    def _is_request_valid(self, request):
        if not request.body:
            return False

        body = json.loads(request.body)
        percent = body.get("percent")
        brand_slug = body.get("brand_slug")
        count = body.get("count")
        if not percent or not brand_slug or not count:
            return False

        return True


@method_decorator(csrf_exempt, name='dispatch')
class GetDiscountCode(View):
    def post(self, request):
        # Login required, Auth service would've set the username header if user was logged in.
        username = request.headers.get('username')
        if not username:
            return HttpResponseForbidden()

        if not self._is_request_valid(request):
            return HttpResponseBadRequest()

        body = json.loads(request.body)
        brand_slug = body['brand_slug']
        dc, error = reserve_discount_code_retry_race_condition(
            brand_slug=brand_slug, username=username
        )
        if error:
            return HttpResponseServerError()
        if not dc:
            return HttpResponseNotFound()

        return HttpResponse(dc.discount_code)

    def _is_request_valid(self, request):
        if not request.body:
            return False
        body = json.loads(request.body)
        brand_slug = body.get("brand_slug")
        if not brand_slug:
            return False

        return True
