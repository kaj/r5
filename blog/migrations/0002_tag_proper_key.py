# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaggedPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='blog.Post')),
                ('tag', models.ForeignKey(related_name='blog_taggedpost_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='blog.TaggedPost', help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
