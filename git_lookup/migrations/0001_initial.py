# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Packages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=254)),
                ('version', models.CharField(default=b'', max_length=254)),
                ('count', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('repo_name', models.CharField(max_length=254)),
                ('owner', models.CharField(max_length=254)),
                ('package', models.ManyToManyField(to='git_lookup.Packages', null=True)),
            ],
        ),
    ]
