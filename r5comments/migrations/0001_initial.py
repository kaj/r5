# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('by_name', models.CharField(max_length=100)),
                ('by_email', models.EmailField(max_length=75, db_index=True)),
                ('by_url', models.URLField(null=True)),
                ('comment', models.TextField()),
                ('submit_date', models.DateTimeField(db_index=True)),
                ('by_ip', models.GenericIPAddressField(null=True, db_index=True)),
                ('is_removed', models.BooleanField(default=False, db_index=True)),
                ('is_public', models.BooleanField(default=False, db_index=True)),
                ('post', models.ForeignKey(to='blog.Post')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
