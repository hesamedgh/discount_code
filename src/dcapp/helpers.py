import string
import random
import logging

from django.db import transaction
from django.db.utils import (
    IntegrityError, OperationalError
)
from django.conf import settings

from dcapp.models import DiscountCode

logger = logging.getLogger(__name__)


def create_discount_codes_with_retry_for_uniqueness(brand_slug: str, percent: int, count: int) -> bool:
    created = False
    retry_count = 0
    while (not created and retry_count < settings.DCAPP_MAX_UNIQUENESS_RETRY_COUNT):
        try:
            create_discount_codes(brand_slug, percent, count)
            created = True
        except IntegrityError:
            retry_count += 1
        except Exception as e:
            logger.error(str(e))
            return False

    if not created:
        logger.warning(
            "Could not create discount codes, reached max_uniqueness_retry"
        )

    return created


def create_discount_codes(brand_slug: str, percent: int, count: int):
    objects = []
    for _ in range(count):
        discount_code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=settings.DCAPP_DISCOUNT_CODE_LENGTH)
        )
        objects.append(
            DiscountCode(
                discount_code=discount_code,
                brand_slug=brand_slug,
                discount_percent=percent
            )
        )
    DiscountCode.objects.bulk_create(objects)


def reserve_discount_code_retry_race_condition(brand_slug: str, username: str) -> (DiscountCode, Exception):
    retry_count = 0
    reserved = None
    while (not reserved and retry_count < settings.DCAPP_MAX_RESERVE_RETRY_COUNT):
        try:
            reserved = reserve_discount_code(brand_slug=brand_slug, username=username)
            if not reserved:  # No discount codes left.
                return None, None
            else:  # discount code found.
                return reserved, None
        except OperationalError:  # Failed getting row lock due to race condition.
            retry_count += 1
        except Exception as e:  # Failed with unexpected error.
            logger.error(e)
            return None, e

    logger.warning(
        "Could not reserve discount code, reached max_reserve_retry"
    )
    return None, DiscountCode.IntegrityError()


def reserve_discount_code(brand_slug: str, username: str) -> DiscountCode:
    dc = DiscountCode.objects.filter(
            brand_slug=brand_slug, reserved_by=None
    ).first()
    if not dc:
        return None

    with transaction.atomic():
        dc = DiscountCode.objects.select_for_update(nowait=True).get(pk=dc.pk)
        dc.reserved_by = username
        dc.save()
    return dc
