# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('git_lookup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='packages',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 13, 10, 29, 41, 418318, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='repo',
            unique_together=set([('repo_name', 'owner')]),
        ),
    ]
