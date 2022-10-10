from django.db import models


class DiscountCode(models.Model):
    brand_slug = models.CharField(max_length=50)
    discount_code = models.CharField(max_length=10)
    reserved_by = models.CharField(max_length=100, null=True)
    discount_percent = models.IntegerField()

    class Meta:
        unique_together = ('brand_slug', 'discount_code',)
