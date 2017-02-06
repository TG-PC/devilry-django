# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-02-06 11:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devilry_group', '0026_datamigrate_update_for_no_none_values_in_feedbackset_deadline'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackSetDeadlineHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deadline_old', models.DateTimeField()),
                ('deadline_new', models.DateTimeField()),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='feedbackset',
            name='deadline_datetime',
            field=models.DateTimeField(),
        ),
        migrations.AddField(
            model_name='feedbacksetdeadlinehistory',
            name='feedback_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='devilry_group.FeedbackSet'),
        ),
    ]
