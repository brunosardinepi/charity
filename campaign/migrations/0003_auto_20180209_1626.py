# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-09 22:26
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_auto_20180209_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='goal',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2147483647)]),
        ),
    ]