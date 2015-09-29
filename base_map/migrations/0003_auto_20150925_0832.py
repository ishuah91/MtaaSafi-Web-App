# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base_map.models.shapes
import jsonfield.fields

def create_default_group(apps, schema_editor):
    AdministrativeGroup = apps.get_model('base_map', 'AdministrativeGroup')
    AdministrativeGroup.objects.create(name='Default', adminType='arbitrary')

def delete_default_group(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('base_map', '0002_basesite'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrativeGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('adminType', models.CharField(max_length=255)),
                ('topojson', jsonfield.fields.JSONField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='AdministrativeUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('divisionType', models.CharField(max_length=255)),
                ('neighbors', models.ManyToManyField(related_name='neighbors_rel_+', to='base_map.AdministrativeUnit')),
            ],
            bases=(base_map.models.shapes.ShapeMixin, models.Model),
        ),
        migrations.AddField(
            model_name='administrativegroup',
            name='administrativeUnits',
            field=models.ManyToManyField(to='base_map.AdministrativeUnit', blank=True),
        ),
        migrations.RunPython(create_default_group, delete_default_group)
    ]
