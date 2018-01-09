# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-09 04:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_auto_20180108_2222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='object_pk',
        ),
        migrations.AddField(
            model_name='comment',
            name='object_id',
            field=models.PositiveIntegerField(default='1'),
            preserve_default=False,
        ),
    ]
