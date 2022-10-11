from datetime import timedelta

from django.contrib import admin
from django.urls import path

from ratelimiter import simple_limiter_singleton

from dcapp.views import (
    GenerateDiscountCode,
    GetDiscountCode,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate-dc/', GenerateDiscountCode.as_view()),
    path('get-dc/', GetDiscountCode.as_view(
            rate_limiter=simple_limiter_singleton
        )
    ),
]
