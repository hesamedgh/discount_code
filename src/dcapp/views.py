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

from ratelimiter.limiter import LimiterAbstractClass

from dcapp.utils import (
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
    rate_limiter = None

    def __init__(self, rate_limiter: LimiterAbstractClass):
        self.rate_limiter = rate_limiter

    def post(self, request):
        # Login required.
        # Auth service would've set the username header if user was logged in.
        username = request.headers.get('username')
        if not username:
            return HttpResponseForbidden()

        if not self._is_request_valid(request):
            return HttpResponseBadRequest()

        body = json.loads(request.body)
        brand_slug = body['brand_slug']

        # Check user is not limited to get code.
        if self.rate_limiter and not self.rate_limiter.can_user_get_discount_code(
            brand_slug=brand_slug, username=username
        ):
            return HttpResponseForbidden("rate limited.")

        # Get code, avoid race condition and giving 1 code to 2 users.
        dc, error = reserve_discount_code_retry_race_condition(
            brand_slug=brand_slug, username=username
        )
        if error:
            return HttpResponseServerError()
        if not dc:
            return HttpResponseNotFound()

        # Update rate limiter and add the new time for this user.
        if self.rate_limiter:
            self.rate_limiter.set_new_get_code_time(
                brand_slug=brand_slug, username=username
            )

        return HttpResponse(dc.discount_code)

    def _is_request_valid(self, request):
        if not request.body:
            return False
        body = json.loads(request.body)
        brand_slug = body.get("brand_slug")
        if not brand_slug:
            return False

        return True
