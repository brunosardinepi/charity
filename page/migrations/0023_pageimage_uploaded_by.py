# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-27 18:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('page', '0022_pageimage_uploaded_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageimage',
            name='uploaded_by',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
