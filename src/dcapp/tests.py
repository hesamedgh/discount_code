from unittest.mock import patch

from django.test import TestCase

from dcapp.models import DiscountCode


class GenerateDiscountCodeTestCase(TestCase):
    def test_generate_discount_code(self):
        response = self.client.post(
            '/generate-dc/',
            data={
                "brand_slug": "test_brand",
                "count": 10,
                "percent": 25
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            DiscountCode.objects.filter(
                brand_slug="test_brand", discount_percent="25"
            ).count(),
            10
        )


class GetDiscountCodeTestCase(TestCase):
    def setUp(self):
        self.dc = DiscountCode.objects.create(
            brand_slug='test_brand',
            discount_percent=25,
            discount_code="test_code"
        )

    def test_login_required(self):
        response = self.client.post(
            '/get-dc/',
            data={"brand_slug": self.dc.brand_slug},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_no_code_found(self):
        response = self.client.post(
            '/get-dc/',
            data={"brand_slug": "nonexistant_brand"},
            content_type="application/json",
            HTTP_USERNAME="test_user"
        )
        self.assertEqual(response.status_code, 404)

    def test_get_discount_code(self):
        response = self.client.post(
            '/get-dc/',
            data={"brand_slug": "test_brand"},
            content_type="application/json",
            HTTP_USERNAME="test_user"
        )
        self.dc.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), self.dc.discount_code)
        self.assertEqual(self.dc.reserved_by, "test_user")

    def test_rate_limit(self):
        with patch('ratelimiter.simple_limiter_singleton.can_user_get_discount_code', return_value=False):
            response = self.client.post(
                '/get-dc/',
                data={"brand_slug": "test_brand"},
                content_type="application/json",
                HTTP_USERNAME="test_user"
            )
            self.assertEqual(response.status_code, 403)
