import logging
import json
from lxml import etree
from collections import namedtuple
from itertools import chain
from lazy.lazy import lazy
from xblock.core import XBlock
from xblock.exceptions import NoSuchViewError, JsonHandlerError
from xblock.fields import Boolean, Scope, String, Integer, Float, List, ScopeIds
from xblock.fragment import Fragment
from xblock.runtime import MemoryIdManager

from xblock.validation import Validation
from xblockutils.helpers import child_isinstance
from xblockutils.resources import ResourceLoader
from xblockutils.settings import XBlockWithSettingsMixin, ThemableXBlockMixin
#from xmodule.modulestore.xml import CourseLocationManager
from uuid import uuid4
from opaque_keys.edx.keys import CourseKey
from .models import Templates
from xblock.validation import ValidationMessage
from xblockutils.studio_editable import (
    NestedXBlockSpec, StudioEditableXBlockMixin, StudioContainerWithNestedXBlocksMixin,
    )
from .question_generator_block import QuestionGeneratorXBlock
try: 
    from workbench.runtime import WorkbenchRuntime
except ImportError:
    WorkbenchRuntime = False



log =logging.getLogger(__name__)
loader = ResourceLoader(__name__)


def _(text):
    return text

class QuestionAnswerXBlock( StudioContainerWithNestedXBlocksMixin, XBlock, StudioEditableXBlockMixin):
    CATEGORY ='tb-question-answer'
    STUDIO_LABEL = _(u'Parsed Question-Answer')
    
    display_name = String (
        display_name = _(u'Question Answer'),
        scope = Scope.settings,
        default = _(u'Question - Answer')
    )
    question = String (
        display_name = _(u'Question'),
        scope = Scope.content,
        default = None,
        multiline_editor=True
    )
    answer = String (
        display_name = _(u'Answer'),
        scope = Scope.content,
        default = None,
        multiline_editor  = True
    )
    editable_fields = ('display_name', 'question', 'answer')

    @property
    def allowed_nested_blocks(self):
        return [QuestionGeneratorXBlock]
    def get_models_object(self):
        templates = None
        try:
            templates = Templates.objects.get(block_id = self.parent)
            log.error("This block {%s} have been created ", self.parent)
        except Templates.DoesNotExist:
            log.error(u'This block has not created yet')
            obj = Templates.objects.create(block_id = self.parent)
            templates = Templates.objects.get(block_id = self.parent)
        templates.outer_block_id1 = self.scope_ids.usage_id
        templates.save()
        return templates
    def studio_view(self, context):
        templates = self.get_models_object()
        q = templates.parsed_question
        a = templates.parsed_answer
        setattr(self, 'question', q)
        setattr(self, 'answer', a)
        frag = super(QuestionAnswerXBlock, self).studio_view(context)
        return frag
    def author_edit_view(self, context):
        frag = super(QuestionAnswerXBlock, self).author_edit_view(context)
        return frag
    def student_view(self, context = None):
        templates = self.get_models_object()
        log.error("templates.parsed_question : %s", templates.parsed_question)
        log.error("templates.parsed_answer: %s", templates.parsed_answer)
        context = {
              'question' : templates.parsed_question,
               'answer' : templates.parsed_answer
        }
        frag = Fragment() 
        frag.add_content(loader.render_template('templates/question_template.html', context)) 
        return frag
class FancyXBlock(StudioContainerWithNestedXBlocksMixin, XBlock, StudioEditableXBlockMixin):
    CATEGORY = 'tb-fancy'
    STUDIO_LABEL = _(u"Question")
    display_name = String (
        display_name = _("Title"),
        scope = Scope.settings,
        default = _("Original Question")
    )
    question = String (
        display_name = _("question"),
        scope = Scope.content,
        default = None,
        multiline_editor = True
    )
    editable_fields = ('display_name', 'question')

    @property
    def allowed_nested_blocks(self):
        return [QuestionAnswerXBlock]

    def student_view(self, context = None):
        templates = self.get_models_object()
        log.error("templates.parsed_question : %s", templates.parsed_question)
        log.error("templates.parsed_answer: %s", templates.parsed_answer)
        context = {
            'question' : templates.parsed_question,
            'answer' : templates.parsed_answer
        }
        frag = Fragment()
                
        frag.add_content(loader.render_template('templates/question_template.html', context))
        
        return frag
    def get_models_object(self):
        templates = None
        try:
            templates = Templates.objects.get(block_id = self.scope_ids.usage_id)
            log.error("This block {%s} have been created ", self.scope_ids.usage_id)
        except Templates.DoesNotExist:
            log.error(u'This block has not created yet')
            obj = Templates.objects.create(block_id = self.scope_ids.usage_id)
            templates = Templates.objects.get(block_id = self.scope_ids.usage_id)
        templates.course_key = getattr(self.runtime, 'course_id', 'all')
        templates.outermost_block_id = self.parent
        templates.question = self.question
        templates.save()
        return templates

    def validate_field_data(self, validation, data):
        """""
        Ask this xblock to validate itself.
        XBlock subclass are expected to override this method. Any overiding method should call super() to collect 
        validation results from its superclass, and then add any additional results as necesary.
        """""
        super(FancyXBlock, self).validate_field_data(validation, data)
        models = self.get_models_object()
        def add_error(msg):
            validation.add(ValidationMessage(ValidationMessage.ERROR, msg))
        def add_warning(msg):
            validation.add(ValidationMesssage(ValidationMessage.WARNING, msg))
        if data.question is None or data.question == "None" or data.question == "":
            add_error(u'Please input a question along with answer into Question Text Box. Otherwise nothing can be done')
        import re
        answer_string = re.search(r'Answer:', data.question)
        models.question = data.question
        if answer_string is None:
            add_warning(u'There is no answer yet. Please help to fill it separating by "Answer:". Otherwise We cannot process futher')
            models.parsed_answer = None
            models.parsed_question = data.question
        else:
            text_list = re.split(r'Answer:', data.question)
            models.parsed_question = text_list[0]
            models.parsed_answer = text_list[1]
            log.error("models.parsed_question = %s, models.parsed_answer = %s", models.parsed_question, models.parsed_answer)
        models.save()

    def author_edit_view(self, context = None):
        frag = super(FancyXBlock, self).author_edit_view(context)
        return frag


class TemplateBlock(StudioContainerWithNestedXBlocksMixin, XBlock, StudioEditableXBlockMixin):
    display_name = String (
        display_name = _("Title"),
        help =_("The title of this Xblock"),
        scope = Scope.settings,
        default = _("Stuff")
        )
    question = Integer (
        display_name = _("Maximun Question"),
        default = 1,
        scope = Scope.settings,
        )
    editable_fields = ('display_name', 'question')

    @property
    def allowed_nested_blocks(self):

        return [FancyXBlock] 

    def validate_field_data(self, validation, data):
        """""
        Ask this xblock to validate itself.
        XBlock subclass are expected to override this method. Any overiding method should call super() to collect 
        validation results from its superclass, and then add any additional results as necesary.
        """""
        super(TemplateBlock, self).validate_field_data(validation, data)
        def add_error(msg):
            validation.add(ValidationMessage(ValidationMessage.ERROR, msg))

    def author_edit_view(self, context = None):
        frag = super(TemplateBlock, self).author_edit_view(context)
        return frag
    def student_view(self, context):
        children_contents = []
        fragment = Fragment()
        for child_id in self.children:
            child = self.runtime.get_block(child_id)
            for sub_child_id in child.children:
                sub_child = self.runtime.get_block(sub_child_id)
                for super_sub_child_id in sub_child.children:
                    super_sub_child = self.runtime.get_block(super_sub_child_id)
                    child_fragment = self._render_child_fragment(super_sub_child, context, 'student_view')
                    fragment.add_frag_resources(child_fragment)
                    children_contents.append(child_fragment.content)
        
        render_context = {
            'block': self,
            'children_contents': children_contents
        }
        render_context.update(context)
        fragment.add_content(self.loader.render_template(self.CHILD_PREVIEW_TEMPLATE, render_context))
        return fragment

       
