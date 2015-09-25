# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base_map.models.shapes
import datetime
import django.db.models.deletion
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_map', '0003_auto_20150925_0832'),
        ('gcm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('region_type', models.CharField(default=b'', max_length=100)),
                ('region_parent', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web_app.Admin', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(base_map.models.shapes.ShapeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=55)),
                ('description', models.CharField(max_length=255)),
                ('admins', models.ManyToManyField(related_name='admins', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Landmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('place_type', models.CharField(max_length=50)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(base_map.models.shapes.ShapeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'mtaasafi', blank=True)),
                ('timestamp', models.DateTimeField()),
                ('sha1_hash', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='MtaaSafiUserMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('google_user_id', models.CharField(max_length=255, null=True, blank=True)),
                ('facebook_user_id', models.CharField(max_length=255, null=True, blank=True)),
                ('whereabouts', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('last_update_timestamp', models.DateTimeField(default=datetime.datetime(2010, 1, 1, 0, 0))),
                ('device', models.ForeignKey(blank=True, to='gcm.Device', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('basesite_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_map.BaseSite')),
                ('description', models.TextField()),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Broken'), (1, b'In Progress'), (2, b'Fixed')])),
                ('corrupt_flag', models.BooleanField(default=False)),
                ('incomplete_flag', models.BooleanField(default=True)),
                ('last_update_timestamp', models.DateTimeField(null=True, blank=True)),
                ('location_accuracy', models.FloatField(null=True, blank=True)),
                ('location_timestamp', models.DateTimeField(null=True, blank=True)),
                ('location_provider', models.CharField(max_length=20, null=True, blank=True)),
                ('geo_admin', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base_map.AdministrativeUnit', null=True)),
                ('landmark', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web_app.Landmark', null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, to='web_app.Report', null=True)),
            ],
            bases=('base_map.basesite',),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UpVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(to='web_app.Report')),
            ],
        ),
        migrations.AddField(
            model_name='report',
            name='tags',
            field=models.ManyToManyField(to='web_app.Tag'),
        ),
        migrations.AddField(
            model_name='report',
            name='user_admin',
            field=models.ForeignKey(related_name='user_report_set', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='web_app.Admin', null=True),
        ),
        migrations.AddField(
            model_name='media',
            name='report',
            field=models.ForeignKey(to='web_app.Report'),
        ),
        migrations.AddField(
            model_name='group',
            name='reports',
            field=models.ManyToManyField(related_name='reports', to='web_app.Report'),
        ),
        migrations.AddField(
            model_name='comment',
            name='report',
            field=models.ForeignKey(to='web_app.Report'),
        ),
        migrations.AlterUniqueTogether(
            name='upvote',
            unique_together=set([('owner', 'report')]),
        ),
    ]
