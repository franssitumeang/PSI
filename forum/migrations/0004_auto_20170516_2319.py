# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 16:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20170515_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='t_komentar',
            fields=[
                ('id_komentar', models.IntegerField(primary_key=True, serialize=False)),
                ('isi_komentar', models.TextField()),
                ('date_created_komentar', models.DateTimeField(auto_now_add=True)),
                ('email', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='forum.t_user')),
                ('id_topik', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='forum.t_topik')),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='room',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='Room',
        ),
    ]
