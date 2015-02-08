# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(unique=True, max_length=50, db_index=True)),
                ('sourcename', models.CharField(unique=True, max_length=100, db_index=True)),
                ('orig_width', models.IntegerField()),
                ('orig_height', models.IntegerField()),
                ('mimetype', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('posted_time', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('title', models.CharField(max_length=200)),
                ('abstract', models.TextField(blank=True)),
                ('content', models.TextField()),
                ('frontimage', models.TextField(blank=True)),
                ('lang', models.CharField(max_length=2, db_index=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['-posted_time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(db_index=True)),
                ('note', models.TextField(blank=True)),
                ('post', models.ForeignKey(to='blog.Post')),
            ],
            options={
                'ordering': ['-time'],
            },
            bases=(models.Model,),
        ),
    ]
