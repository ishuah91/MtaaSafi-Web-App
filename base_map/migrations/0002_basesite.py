# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base_map.models.shapes


class Migration(migrations.Migration):

    dependencies = [
        ('base_map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'temp', max_length=100)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('text', models.CharField(max_length=500, null=True, blank=True)),
                ('picture', models.ImageField(upload_to=b'img', blank=True)),
            ],
            options={
                'db_table': 'base_map_basesite',
                'verbose_name': 'site',
            },
            bases=(base_map.models.shapes.ShapeMixin, models.Model),
        ),
    ]
