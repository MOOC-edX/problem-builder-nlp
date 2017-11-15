# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem_template_builder', '0003_matlabquestion_questionnode'),
    ]

    operations = [
        migrations.AddField(
            model_name='matlabquestion',
            name='generated_answer',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='matlabquestion',
            name='generated_question',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='matlabquestion',
            name='generated_variable',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
