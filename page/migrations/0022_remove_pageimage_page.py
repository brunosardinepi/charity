# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-11 18:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0021_pageimage_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pageimage',
            name='page',
        ),
    ]
