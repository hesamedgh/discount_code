# Generated by Django 3.0.5 on 2022-10-10 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_slug', models.CharField(max_length=50)),
                ('discount_code', models.CharField(max_length=10)),
                ('reserved_by', models.CharField(max_length=100, null=True)),
                ('discount_percent', models.IntegerField()),
            ],
            options={
                'unique_together': {('brand_slug', 'discount_code')},
            },
        ),
    ]
