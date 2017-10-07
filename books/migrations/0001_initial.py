# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lt_slug', models.CharField(unique=True, max_length=32, db_index=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lt_id', models.CharField(unique=True, max_length=16, db_index=True)),
                ('title', models.CharField(max_length=200, db_index=True)),
                ('cover', models.URLField(null=True, blank=True)),
                ('lang', models.CharField(max_length=3, db_index=True)),
                ('rating', models.PositiveSmallIntegerField(help_text=b'LT rating times 10', db_index=True)),
                ('author', models.ForeignKey(to='books.Author', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='BookTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='books.Book', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(related_name='books_taggedbook_items', to='books.BookTag', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='book',
            name='tags',
            field=taggit.managers.TaggableManager(to='books.BookTag', through='books.TaggedBook', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
