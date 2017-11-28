# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-28 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0019_remove_campaign_vote_winner_gets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='type',
            field=models.CharField(choices=[('event', 'Event'), ('general', 'General'), ('vote', 'Vote')], default='General', max_length=255),
        ),
    ]
