# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2015 Harvard, edX & OpenCraft
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

# Imports ###########################################################

from django.db import models
from django.contrib.auth.models import User


# Classes ###########################################################

class Templates(models.Model):
    """
    Django model used to store AnswerBlock data that need to be shared
    and queried accross XBlock instances (workaround).

    TODO: Deprecate this and move to edx-submissions
    """

    block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    # course_id is deprecated; it will be removed in next release.
    inner_block_id1 = models.CharField(max_length=512, db_index=True, blank=True, null=True, default=None)
    # course_key is the new course_id replacement with extended max_length.
    course_key = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    inner_block_id2 = models.CharField(max_length=512, db_index=True, blank=True, null=True, default=None)
    inner_block_id3 = models.CharField(max_length=515, db_index=True, blank=True, null=True, default=None)
    inner_block_id4 = models.CharField(max_length=512, db_index=True, blank=True, null=True, default=None)
    teacher_question = models.TextField(blank=True, default=None, null=True)
    parsed_question = models.TextField(blank=True, default = None, null=True)
    parsed_answer = models.TextField(blank=True, default= None, null=True)
    parsed_question1 = models.TextField(blank=True, default=None, null=True)
    parsed_answer1 = models.TextField(blank=True, default=None, null=True)
    image_link=models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    list_variables = models.TextField(blank=True, default=None, null=True)
    outermost_block_id = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    outer_block_id1 = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    outer_block_id2 = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    outer_block_id3 = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    outer_block_id4 = models.CharField(max_length=255, db_index=True, blank=True, null=True, default=None)
    def save(self, *args, **kwargs):
        # Force validation of max_length
        self.full_clean()
        super(Templates, self).save(*args, **kwargs)

class QuestionNode(models.Model):
    block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    next_block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    pre_block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    outermost_block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    input_question = models.TextField(blank=True, default=None, null=True)
    input_answer = models.TextField(blank=True, default=None, null=True)
    image_url = models.TextField(blank=True, default=None, null=True)
    parsed_question = models.TextField(blank=True, default=None, null=True)
    parsed_answer = models.TextField(blank=True, default=None, null=True)
    parsed_number_variables = models.TextField(blank=True, default=None, null=True)
    parsed_string_variables = models.TextField(blank=True, default=None, null=True)
    def save(self, *args, **kwargs):
        self.full_clean()
        super(QuestionNode, self).save(*args, **kwargs)
class MatlabQuestion(models.Model):
    block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    question_template = models.TextField(blank=True, default=None, null=True)
    answer_template = models.TextField(blank=True, default=None, null=True)
    variables = models.TextField(blank=True, default=None, null=True)
    image_url = models.TextField(blank=True, default=None, null=True)
    outermost_block_id = models.CharField(max_length=255, db_index=True, blank=True, default=None, null=True)
    generated_variable = models.TextField(blank=True, default=None, null=True)
    generated_question = models.TextField(blank=True, default=None, null=True)
    generated_answer = models.TextField(blank=True, default=None, null=True)
    def save(self, *args, **kwargs):
        self.full_clean()
        super(MatlabQuestion, self).save(*args, **kwargs)
