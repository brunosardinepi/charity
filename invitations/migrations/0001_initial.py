# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-23 20:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import invitations.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expired', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
                ('key', models.CharField(default=invitations.models.random_key, max_length=32)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('invite_to', models.EmailField(max_length=254)),
                ('can_edit', models.BooleanField(default=False)),
                ('can_delete', models.BooleanField(default=False)),
                ('can_invite', models.BooleanField(default=False)),
                ('invite_from', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
