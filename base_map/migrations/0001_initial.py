# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shape',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'base_map_shape',
            },
        ),
        migrations.CreateModel(
            name='Line',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
            ],
            options={
                'db_table': 'base_map_line',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='MultiLine',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            options={
                'db_table': 'base_map_multiline',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='MultiPolygon',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'db_table': 'base_map_multipolygon',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='MultiPolygon3D',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, dim=3)),
            ],
            options={
                'db_table': 'base_map_multipolygon3d',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'db_table': 'base_map_point',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='Polygon',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
                'db_table': 'base_map_polygon',
            },
            bases=('base_map.shape',),
        ),
        migrations.CreateModel(
            name='Polygon3D',
            fields=[
                ('shape_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.Shape')),
                ('shape', django.contrib.gis.db.models.fields.PolygonField(srid=4326, dim=3)),
            ],
            options={
                'db_table': 'base_map_polygon3d',
            },
            bases=('base_map.shape',),
        ),
        migrations.AddField(
            model_name='shape',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AlterUniqueTogether(
            name='shape',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
