# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-01-04 05:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devilry_group', '0022_auto_20170103_2308'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedbackset',
            name='is_last_in_group',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='feedbackset',
            unique_together=set([('group', 'is_last_in_group')]),
        ),
    ]
