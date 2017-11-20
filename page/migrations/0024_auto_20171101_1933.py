# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-02 00:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0023_pageimage_uploaded_by'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'permissions': (('manager_edit', 'Manager -- edit Page'), ('manager_delete', 'Manager -- delete Page'), ('manager_invite', 'Manager -- invite users to manage Page'), ('manager_image_edit', 'Manager -- upload and edit media on Page'), ('manager_view_dashboard', 'Manager -- view Page dashboard'))},
        ),
    ]