# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('r5comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['submit_date']},
        ),
        migrations.AlterField(
            model_name='comment',
            name='by_email',
            field=models.EmailField(help_text='Not published, except as gravatar.', max_length=254, verbose_name='Email', db_index=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='by_name',
            field=models.CharField(help_text='Your name (or pseudonym).', max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='by_url',
            field=models.URLField(help_text='Your homepage / presentation.', null=True, verbose_name='URL', blank=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(help_text='No formatting, except that an empty line is interpreted as a paragraph break.', verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='submit_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
