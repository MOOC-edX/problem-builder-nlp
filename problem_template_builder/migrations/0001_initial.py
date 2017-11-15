# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
#
# from django.db import migrations, models
#
#
# class Migration(migrations.Migration):
#
#     dependencies = [
#     ]
#
#     operations = [
#         migrations.CreateModel(
#             name='Templates',
#             fields=[
#                 ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
#                 ('block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('inner_block_id1', models.CharField(default=None, max_length=512, null=True, db_index=True, blank=True)),
#                 ('course_key', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('inner_block_id2', models.CharField(default=None, max_length=512, null=True, db_index=True, blank=True)),
#                 ('inner_block_id3', models.CharField(default=None, max_length=515, null=True, db_index=True, blank=True)),
#                 ('inner_block_id4', models.CharField(default=None, max_length=512, null=True, db_index=True, blank=True)),
#                 ('teacher_question', models.TextField(default=None, null=True, blank=True)),
#                 ('parsed_question', models.TextField(default=None, null=True, blank=True)),
#                 ('parsed_answer', models.TextField(default=None, null=True, blank=True)),
#                 ('parsed_question1', models.TextField(default=None, null=True, blank=True)),
#                 ('parsed_answer1', models.TextField(default=None, null=True, blank=True)),
#                 ('image_link', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('list_variables', models.TextField(default=None, null=True, blank=True)),
#                 ('outermost_block_id', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('outer_block_id1', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('outer_block_id2', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('outer_block_id3', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#                 ('outer_block_id4', models.CharField(default=None, max_length=255, null=True, db_index=True, blank=True)),
#             ],
#         ),
#     ]
