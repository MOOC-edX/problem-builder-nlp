# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem_template_builder', '0002_auto_20170829_0501'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatlabQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('question_template', models.TextField(default=None, null=True, blank=True)),
                ('answer_template', models.TextField(default=None, null=True, blank=True)),
                ('variables', models.TextField(default=None, null=True, blank=True)),
                ('image_url', models.TextField(default=None, null=True, blank=True)),
                ('outermost_block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('next_block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('pre_block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('outermost_block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
                ('input_question', models.TextField(default=None, null=True, blank=True)),
                ('input_answer', models.TextField(default=None, null=True, blank=True)),
                ('image_url', models.TextField(default=None, null=True, blank=True)),
                ('parsed_question', models.TextField(default=None, null=True, blank=True)),
                ('parsed_answer', models.TextField(default=None, null=True, blank=True)),
                ('parsed_number_variables', models.TextField(default=None, null=True, blank=True)),
                ('parsed_string_variables', models.TextField(default=None, null=True, blank=True)),
            ],
        ),
    ]
