# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-30 16:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0024_auto_20171101_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='donation_count',
        ),
        migrations.RemoveField(
            model_name='page',
            name='donation_money',
        ),
    ]