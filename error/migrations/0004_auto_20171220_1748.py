# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-20 23:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('error', '0003_auto_20171220_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='error',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]