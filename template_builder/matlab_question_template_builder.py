"""TO-DO: Write a description of what this XBlock is."""

import sys
import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, JSONField, Integer, String, Boolean, Dict, List
from xblock.fragment import Fragment

from xblock.exceptions import JsonHandlerError, NoSuchViewError
from xblock.validation import Validation

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin, FutureFields
from xblockutils.resources import ResourceLoader

import matlab_service
import matlab_question_service
import qgb_db_service
import json
from resolver_machine import resolver_machine
import logging
# import xblock_deletion_handler
from question_parser import parse_question_v2, parse_answer_v2, parse_question_improved, parse_answer_improved
import qgb_question_service
import xml_helper

loader = ResourceLoader(__name__)

# Constants
ADVANCED_EDITOR_NAME = 'Advanced Editor'
SIMPLE_EDITOR_NAME = 'Simple Template'

def _(text):
    return text


@XBlock.needs("i18n")
class MatlabQuestionTemplateBuilderXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    Question Generator XBlock
    """
    #
    CATEGORY = 'tb-matlab-question-template-builder'
    STUDIO_LABEL = _(u'Question from Natural Language')

    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Question from Natural Language"
    )

    max_attempts = Integer(
        display_name="Maximum Attempts",
        help="Defines the number of times a student can try to answer this problem.",
        default=1,
        values={"min": 1}, scope=Scope.settings)

    max_points = Integer(
        display_name="Possible points",
        help="Defines the maximum points that the learner can earn.",
        default=1,
        scope=Scope.settings)

    show_points_earned = Boolean(
        display_name="Shows points earned",
        help="Shows points earned",
        default=True,
        scope=Scope.settings)

    show_submission_times = Boolean(
        display_name="Shows submission times",
        help="Shows submission times",
        default=True,
        scope=Scope.settings)

    show_answer = Boolean(
        display_name="Show Answer",
        help="Defines when to show the 'Show/Hide Answer' button",
        default=True,
        scope=Scope.settings)

    allow_reset = Boolean(
        display_name="Show Reset Button",
        help="Determines whether a 'Reset' button is shown so the user may reset their answer. A default value can be set in Advanced Settings.",
        default=True,
        scope=Scope.settings)

    #TODO: add comments about scope of these new variables. Why these variables?
    #
    _image_url = String (
        display_name ="image",
        help ="",
        default="",
        scope = Scope.settings)

    _resolver_selection = String(
        display_name = "Resolver Machine",
        help ="",
        default = 'none',
        scope = Scope.content)

    _problem_solver = String(
        display_name = "Problem Solver",
        help = "Select a solver for this problem",
        default = 'matlab',
        scope = Scope.settings,
        values = [
                    {"display_name": "MatLab", "value": "matlab"},
                    {"display_name": "Google Sheets", "value": "gsheet"},
                ]
    )

    _question_template = String (
        display_name = "Question Template",
        help = "",
        default = """Given [a] [string0]s and [b] [string1]s. One [string0] cost [x] USD, one [string1] cost [y] USD.
Calculate the total price of them?""",
        scope = Scope.settings
    )

    _answer_template = Dict(
        display_name="Answer Template",
        help="Teacher has to fill the answer template here!!!",
        default=
            {
                "price": "[a] * [x] + [b] * [y]"
            },
        scope=Scope.settings
    )

    _answer_template_string = String(
        display_name="Answer Template",
        help="Teacher has to fill the answer template here!!!",
        default= '''price = [a] * [x] + [b] * [y]''',
        scope=Scope.settings
    )

    _variables = Dict (
        display_name = "Numeric Variables",
        help = "",
        default =
            {
                'a':{
                        'name': 'a',
                        'original_text': '7',
                        'min_value': 1,
                        'max_value': 10,
                        'type': 'int',
                        'decimal_places': 0
                    },
                'b':{
                        'name': 'b',
                        'original_text': '5',
                        'min_value': 1,
                        'max_value': 20,
                        'type': 'int',
                        'decimal_places': 0
                    },
                'x':{
                        'name': 'x',
                        'original_text': '20000',
                        'min_value': 4500,
                        'max_value': 100000,
                        'type': 'float',
                        'decimal_places': 2
                    },
                'y':{
                        'name': 'y',
                        'original_text': '43500',
                        'min_value': 100001,
                        'max_value': 500000,
                        'type': 'float',
                        'decimal_places': 2
                    }
            },
        scope = Scope.settings
    )

    # Default XML string passed to Advanced Editor's value when create an xBlock
    raw_editor_xml_data = '''
    <problem>
        <description>Given [a] [string0]s and [b] [string1]s. One [string0] cost [x] USD, one [string1] cost [y] USD.
Calculate the total price of them? </description>
        <images>
            <image_url link="">Image</image_url>
        </images>
        <variables>
            <variable name="a" min_value="1" max_value="10" type="int"/>
            <variable name="b" min_value="1" max_value="20" type="int"/>
            <variable name="x" min_value="4500" max_value="100000" type="float" decimal_places="2"/>
            <variable name="y" min_value="100001" max_value="500000" type="float" decimal_places="2"/>
        </variables>
        <answer_templates>
            <answer price = "[a] * [x] + [b] * [y]">Teacher's answer</answer>
        </answer_templates>
        <string_variables>
            <string_variable default="car" name="string0" original_text="car" value="car">
                <context_list>
                    <context name="Synonyms of text 'car' (Default)" select="true">
                        <option>car</option>
                        <option>machine</option>
                        <option>truck</option>
                        <option>auto</option>
                        <option>automobile</option>
                        <option>electric car</option>
                    </context>
                </context_list>
            </string_variable>
            <string_variable default="house" name="string1" original_text="house" value="house">
                <context_list>
                    <context name="Synonyms of text 'house' (Default)" select="true">
                        <option>house</option>
                        <option>palace</option>
                        <option>building</option>
                        <option>land</option>
                        <option>island</option>
                    </context>
                </context_list>
            </string_variable>
        </string_variables>
    </problem>'''

    # This field is to store editor's value to keep for future initilization of xBlock after edit (student_view, studio_view).
    _raw_editor_xml_data = String(
        display_name="Raw edit",
        help="Raw edit fields value for XML editor",
        default=raw_editor_xml_data,
        scope=Scope.content
    )

    _question_text = String (
        scope = Scope.content,
        default="""Given 7 cars and 5 houses. One car costs 20000 USD, one house costs 43500 USD.
Calculate the total price of them?"""
    )

    _answer_text = String (
        scope = Scope.content,
        default = "price = 7 * 20000 + 5 * 43500"
    )

    _string_vars = Dict(
        scope=Scope.content,
        default=
        {
            'string0': {
                'name': 'string0',
                'original_text': 'car',
                'default': 'car',
                'value': 'car',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Synonyms of text 'car' (Default)",
                            'help': "Default context generated from text 'car'",
                            'synonyms': ['car', 'machine', 'truck', 'auto', 'automobile', 'electric car'],
                            'select': 'true',
                        },
                    }
            },
            'string1': {
                'name': 'string1',
                'original_text': 'house',
                'default': 'house',
                'value': 'house',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Synonyms of text 'house' (Default)",
                            'help': "Default context generated from text 'house'",
                            'synonyms': ['house', 'palace', 'building', 'land', 'island'],
                            'select': 'true',
                        },
                    }
            },
        }
    )

    xblock_id = None
    attempt_number = 0
    newly_created_block = True
    has_score = True
    show_in_read_only_mode = True

    editable_fields = ('display_name',
                       '_problem_solver',
                       'max_attempts',
                       'max_points',
                       'show_points_earned',
                       'show_submission_times',
                       'show_answer',
                       'allow_reset',
                       '_raw_editor_xml_data'
                       )

    # problem solver info
    resolver_handling = resolver_machine()
    resolver_selection = resolver_handling.getDefaultResolver()
    matlab_server_url = resolver_handling.getDefaultAddress()
    matlab_solver_url = resolver_handling.getDefaultURL()

    # customed global variables
    image_url = ""
    question_template_string = ""
    variables = {}
    _generated_question = ""
    _generated_variables = {}
    student_answer = ""

    # Define current editor mode
    enable_advanced_editor = False  # True: Editor mode, False: Template mode.

    # Define if original text question parsed yet
    show_parser = Boolean(
        default=False,
        help="Whether to show Parser tab in Studio view",
        scope = Scope.settings
    )

    reset_question = Boolean(
        default=True,
        help="Whether to generate random variables' values of the current xBlock usage for specific One user",
        scope = Scope.user_state
    )

    reset_question_preview = Boolean(
        default=True,
        help="Whether to generate random variables' values of the current xBlock usage for specific One user in Studio preview",
        scope=Scope.user_state
    )

    runtime_generated_question = String(
        default= _question_text,
        help="To store the last runtime generated question of the current xBlock usage for specific One user",
        scope=Scope.user_state
    )

    runtime_generated_answer = String(
        default="",
        help="To store the last runtime generated answer of the current xBlock usage for specific One user",
        scope=Scope.user_state
    )

    runtime_generated_variables = Dict(
        default=_generated_variables,
        help="To store the last runtime generated variables of the current xBlock usage for specific One user",
        scope=Scope.user_state
    )

    runtime_generated_string_variables = Dict(
        default=_string_vars,
        help="To store the last runtime generated string variables of the current xBlock usage for specific One user",
        scope=Scope.user_state
    )

    # Without this flag, studio will use student_view on newly-added blocks :/
    has_author_view = True


    @property
    def point_string(self):
        if self.show_points_earned:
            score = sub_api.get_score(self.student_item_key)
            if score != None:
                return str(score['points_earned']) + ' / ' + str(score['points_possible']) + ' point(s)'

        return str(self.max_points) + ' point(s) possible'

    @property
    def attempt_number_string(self):
        if (self.show_submission_times):
            return "You have submitted " + str(self.attempt_number) + "/" + str(self.max_attempts) + " time(s)"

        return ""


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context):
        """
        The primary view of the MatlabQuestionTemplateBuilderXBlock, shown to students when viewing courses.
        """
        print("## Start FUNCTION student_view() ##")
        print("self.reset_question = {}".format(self.reset_question))
        print("student_view context = {}".format(context))

        context = context

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        should_disbled = ''
        show_reset_button = self.allow_reset

        # generate question from template if necessary
        if self.reset_question == True:
            self._generated_question, self._generated_variables = matlab_question_service.new_problem(
                self._question_template, self._variables, randomization=True)
            # append string variables
            self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
            # Generate answer
            generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
                                                                              self._answer_template_string)
            # update user_state fields
            setattr(self, 'reset_question', False)
            setattr(self, 'runtime_generated_question', self._generated_question)
            setattr(self, 'runtime_generated_variables', self._generated_variables)
            setattr(self, 'runtime_generated_string_variables', self._string_vars)
            setattr(self, 'runtime_generated_answer', generated_answer)
        else:
            self._generated_question = self.runtime_generated_question
            self._generated_variables = self.runtime_generated_variables
        print("self.reset_question = {}".format(self.reset_question))
        print "self.runtime_generated_question = {}".format(self.runtime_generated_question)
        print "self.runtime_generated_answer = {}".format(self.runtime_generated_answer)
        print("self.runtime_generated_variables = {}".format(self.runtime_generated_variables))
        print("self.runtime_generated_string_variables = {}".format(self.runtime_generated_string_variables))


        # Get previous submissions made by student
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        # print("self.student_item_key = {}".format(self.student_item_key))
        print("previous submissions = {}".format(submissions))

        # Only show student's last submission
        # TODO: to figure out how to handle student's previous submissions
        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer'] # saved "answer information"
            print("answer = {}".format(answer))
            self._generated_question = answer['generated_question']
            self.generated_answer = answer['generated_answer']  # teacher's generated answer
            self.student_answer = answer['student_answer'] # student's submitted answer

            # TODO: check what is this block for?
            # Retrived the generated variables of the last submission
            if ('variable_values' in answer): # backward compatibility
                saved_generated_variables = json.loads(answer['variable_values'])
                for var_name, var_value in saved_generated_variables.iteritems():
                    self._generated_variables[var_name] = var_value

            self.attempt_number = latest_submission['attempt_number']
            if (self.attempt_number >= self.max_attempts):
                should_disbled = 'disabled'

        # Serialize some fields in context dictionary before passing to student_view template
        self.serialize_data_to_context(context)

        # Add following fields to context variable
        context['problem_name'] = self.display_name
        context['disabled'] = should_disbled
        context['student_answer'] = self.student_answer
        context['image_url'] = self._image_url
        context['attempt_number'] = self.attempt_number_string
        context['point_string'] = self.point_string
        context['question'] = self._generated_question
        context['xblock_id'] = self.xblock_id
        context['show_answer'] = self.show_answer
        context['show_reset_button'] = show_reset_button

        frag = Fragment()
        frag.content = loader.render_template('static/html/matlab_question_template_builder/student_view.html', context)
        frag.add_css(self.resource_string("static/css/question_generator_block.css"))
        frag.add_javascript(self.resource_string("static/js/matlab_question_template_builder/student_view.js"))
        frag.initialize_js('MatlabQuestionTemplateBuilderXBlock')

        print("student_view context = {}".format(context))
        print("## End FUNCTION student_view() ##")

        return frag

    def author_view(self, context):
        """
        The primary view of the MatlabQuestionTemplateBuilderXBlock, shown to teacher when previewing courses in Studio (preview mode).
        """
        print("## Start FUNCTION author_view() ##")
        print("self.reset_question_preview = {}".format(self.reset_question_preview))
        print("author_view context = {}".format(context))

        context = context

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        should_disbled = ''
        show_reset_button = self.allow_reset

        # generate question from template if necessary
        if self.reset_question_preview == True:
            self._generated_question, self._generated_variables = matlab_question_service.new_problem(
                self._question_template, self._variables, randomization=True)
            # append string variables
            self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
            # Generate answer
            generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
                                                                              self._answer_template_string)
            # update user_state fields
            setattr(self, 'runtime_generated_question', self._generated_question)
            setattr(self, 'runtime_generated_answer', generated_answer)
            setattr(self, 'runtime_generated_variables', self._generated_variables)
            setattr(self, 'runtime_generated_string_variables', self._string_vars)
        else:
            self._generated_question = self.runtime_generated_question
            self._generated_variables = self.runtime_generated_variables

        # # Get previous submissions made by student
        # submissions = sub_api.get_submissions(self.student_item_key, 1)
        # # print("self.student_item_key = {}".format(self.student_item_key))
        # # print("previous submissions = {}".format(submissions))
        #
        # # Only show student's last submission
        # # TODO: to figure out how to handle student's previous submissions
        # if submissions:
        #     latest_submission = submissions[0]
        #
        #     # parse the answer
        #     answer = latest_submission['answer'] # saved "answer information"
        #     # self._generated_question = answer['generated_question']
        #     # self.generated_answer = answer['generated_answer']  # teacher's generated answer
        #     self.student_answer = answer['student_answer'] # student's submitted answer
        #
        #     # TODO: check what is this block for?
        #     # Retrived the generated variables of the last submission
        #     if ('variable_values' in answer): # backward compatibility
        #         saved_generated_variables = json.loads(answer['variable_values'])
        #         for var_name, var_value in saved_generated_variables.iteritems():
        #             self._generated_variables[var_name] = var_value
        #
        #     self.attempt_number = latest_submission['attempt_number']
        #     if (self.attempt_number >= self.max_attempts):
        #         should_disbled = 'disabled'

        # Reset score and previous submissions made by staff (author)
        sub_api.reset_score(self.student_item_key['student_id'], self.student_item_key['course_id'],
                            self.student_item_key['item_id'], clear_state=True)

        # Serialize some fields in context dictionary before passing to student_view template
        self.serialize_data_to_context(context)

        # Add following fields to context variable
        context['disabled'] = should_disbled
        context['student_answer'] = self.student_answer
        context['image_url'] = self._image_url
        context['attempt_number'] = self.attempt_number_string
        context['point_string'] = self.point_string
        context['question'] = self._generated_question
        context['xblock_id'] = self.xblock_id
        context['show_answer'] = self.show_answer
        context['show_reset_button'] = show_reset_button

        frag = Fragment()
        frag.content = loader.render_template('static/html/matlab_question_template_builder/student_view.html', context)
        frag.add_css(self.resource_string("static/css/question_generator_block.css"))
        frag.add_javascript(self.resource_string("static/js/matlab_question_template_builder/student_view.js"))
        frag.initialize_js('MatlabQuestionTemplateBuilderXBlock')

        print("author_view context = {}".format(context))
        print("## End FUNCTION author_view() ##")

        return frag


    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """
        print("## Start FUNCTION studio_view() ##")
        print("context = {}".format(context))

        # if the XBlock has been submitted already then disable the studio_edit screen
        location = self.location.replace(branch=None, version=None)  # Standardize the key in case it isn't already
        item_id=unicode(location)

        # print("self._variables = {}".format(self._variables))
        # print "self._string_vars = {}".format(self._string_vars)

        # Student not yet submit then we can edit the XBlock
        context = {'fields': []}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)

        # print("self.show_parser = {}".format(self.show_parser))

        # self.serialize_data_to_context(context) ??? REMOVE not necessary, remove ???
        context['question_text_origin'] = self._question_text
        context['answer_text_origin'] = self._answer_text

        context['image_url'] = self._image_url
        context['question_template'] = self._question_template
        context['variables'] = self._variables
        context['string_variables'] = self._string_vars
        context['answer_template_string'] = self._answer_template_string
        context['is_submitted'] = 'False'

        # Handle Editor mode
        if self.enable_advanced_editor:
            context['current_editor_mode_name'] = ADVANCED_EDITOR_NAME
            context['next_editor_mode_name'] = SIMPLE_EDITOR_NAME
        else:
            context['current_editor_mode_name'] = SIMPLE_EDITOR_NAME
            context['next_editor_mode_name'] = ADVANCED_EDITOR_NAME
        context['enable_advanced_editor'] = self.enable_advanced_editor

        # Handle Parser tab
        context['show_parser'] = self.show_parser
        if self.show_parser == True:
            context['btn_toggle_parser_text'] = 'Hide Parser'
        else:
            context['btn_toggle_parser_text'] = 'Show Parser'

        # append xml data for raw xml editor
        context['raw_editor_xml_data'] = self._raw_editor_xml_data

        print("context = {}".format(context))

        fragment = Fragment()
        # fragment.content = loader.render_template('static/html/matlab_question_template_builder/problem_edit.html', context)
        fragment.content = loader.render_template('static/html/matlab_question_template_builder/studio_view_updated.html',
                                                  context)
        fragment.add_css(self.resource_string("static/css/question_generator_block_studio_edit.css"))
        # fragment.add_javascript(loader.load_unicode('static/js/matlab_question_template_builder/problem_edit.js'))
        fragment.add_javascript(loader.load_unicode('static/js/matlab_question_template_builder/studio_view_updated.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')

        print("## End FUNCTION studio_view() ##")

        return fragment


    def serialize_data_to_context(self, context):
        """
        Save data to context to re-use later to avoid re-accessing the DBMS
        """
        print("## Start FUNCTION serialize_data_to_context() ##")
        print("## BEFORE ADDING FIELDS ##")
        print("context = {}".format(context))
        # print("self._question_template = {}".format(self._question_template))
        # print("self._image_url = {}".format(self._image_url))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        # print "self._answer_template_string = ", self._answer_template_string


        # Add following fields to context variable
        context['saved_question_template'] = self._question_template
        context['saved_url_image'] = self._image_url
        context['serialized_variables'] = json.dumps(self._variables)
        context['serialized_generated_variables'] = json.dumps(self._generated_variables)
        context['saved_answer_template'] = self._answer_template_string # string
        context['saved_resolver_selection'] = self._problem_solver  # use _problem_solver from editable_fields

        # print("## AFTER, ADDED FIELDS ##")
        print("context = {}".format(context))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        print("## End FUNCTION serialize_data_to_context() ##")


    def deserialize_data_from_context(self, context):
        """
        De-serialize data previously saved to context
        """
        print("## Start FUNCTION deserialize_data_from_context() ##")
        print("## BEFORE ##")
        print("context = {}".format(context))
        print("self._question_template = {}".format(self._question_template))
        print("self._image_url = {}".format(self._image_url))
        print("self.variables = {}".format(self.variables))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        print "self.question_template_string = ", self.question_template_string
        print "self._answer_template_string = ", self._answer_template_string

        self.question_template_string = context['saved_question_template']
        self.image_url = context['saved_url_image']
        # self._answer_template = context['saved_answer_template']
        # self._answer_template_string = context['saved_answer_template']
        self.variables = json.loads(context['serialized_variables'])
        self._generated_variables = json.loads(context['serialized_generated_variables'])
        self.resolver_selection = context['saved_resolver_selection']   # TODO: update this to new field in Settings tab

        print("## AFTER: ##")
        print("self._question_template = {}".format(self.question_template_string))
        print("self.image_url = {}".format(self.image_url))
        print("self.variables = {}".format(self.variables))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        print "self.question_template_string = ", self.question_template_string
        print "self._answer_template_string = ", self._answer_template_string
        print("## End FUNCTION deserialize_data_from_context() ##")


    def load_data_from_dbms(self):
        """
        Load question template data from MySQL
        """

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        self.question_template_string, self.image_url, self.resolver_selection, self.variables, self._answer_template_string = qgb_db_service.fetch_question_template_data(self.xblock_id)


    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """
        print("## Start FUNCTION student_submit() ##")
        print("data = {}".format(data))

        self.deserialize_data_from_context(data)
        print("data = {}".format(data))

        points_earned = 0

        # TODO generate the teacher's answer
        # Generate answer for this submission
        # generated_answer = matlab_question_service.generate_answer(self._generated_variables, self._answer_template)
        # print("generated_answer = {}".format(generated_answer))

        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables, self._answer_template_string)
        print "generated_answer = ", generated_answer

        student_answer = data['student_answer']
        # save the submission
        submission_data = {
            'generated_question': data['saved_generated_question'],
            'student_answer': student_answer,
            'generated_answer': generated_answer,
            'variable_values': data['serialized_generated_variables']
        }
        print "submission_data = {}".format(submission_data)
        print "self.resolver_selection = " + self.resolver_selection

        # call problem grader
        evaluation_result = self.resolver_handling.syncCall(self.resolver_selection, generated_answer, student_answer )
        #evaluation_result = matlab_service.evaluate_matlab_answer(self.matlab_server_url, self.matlab_solver_url, generated_answer, student_answer)

        if evaluation_result == True:
            points_earned = self.max_points

        submission = sub_api.create_submission(self.student_item_key, submission_data)
        sub_api.set_score(submission['uuid'], points_earned, self.max_points)

        submit_result = {}
        submit_result['point_string'] = self.point_string

        # disable the "Submit" button once the submission attempts reach max_attemps value
        self.attempt_number = submission['attempt_number']
        submit_result['attempt_number'] = self.attempt_number_string
        if (self.attempt_number >= self.max_attempts):
            submit_result['submit_disabled'] = 'disabled'
        else:
            submit_result['submit_disabled'] = ''

        print("## End FUNCTION student_submit() ##")

        return submit_result

    @XBlock.json_handler
    def student_submit_handler(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """

        print("## Start FUNCTION student_submit_handler() ##")
        print("data = {}".format(data))

        # self.deserialize_data_from_context(data)

        points_earned = 0

        # # TODO generate the teacher's answer
        # # Generate answer for this submission
        # generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
        #                                                                   self._answer_template_string)
        # print "generated_answer = ", generated_answer

        student_answer = data['student_answer']
        generated_question = self.runtime_generated_question
        generated_answer = self.runtime_generated_answer
        generated_variables = json.dumps(self.runtime_generated_variables)
        generated_string_variables = json.dumps(self.runtime_generated_string_variables)


        # save the submission
        # submission_data = {
        #     'generated_question': data['saved_generated_question'],
        #     'student_answer': student_answer,
        #     'generated_answer': generated_answer,
        #     'variable_values': data['serialized_generated_variables']
        # }
        submission_data = {
            'generated_question': generated_question,
            'student_answer': student_answer,
            'generated_answer': generated_answer,
            'variable_values': generated_variables
        }

        print "submission_data = {}".format(submission_data)
        print "self.resolver_selection = " + self.resolver_selection
        print "self._problem_solver = " + self._problem_solver

        # call problem grader
        # evaluation_result = self.resolver_handling.syncCall(self.resolver_selection, generated_answer, student_answer)
        evaluation_result = self.resolver_handling.syncCall(self._problem_solver, generated_answer, student_answer)

        if evaluation_result == True:
            points_earned = self.max_points

        submission = sub_api.create_submission(self.student_item_key, submission_data)
        sub_api.set_score(submission['uuid'], points_earned, self.max_points)

        submit_result = {}
        submit_result['point_string'] = self.point_string
        self.attempt_number = submission['attempt_number']
        submit_result['attempt_number'] = self.attempt_number_string
        # Disable the "Submit" button once the submission attempts reach max_attemps value
        if (self.attempt_number >= self.max_attempts):
            submit_result['submit_disabled'] = 'disabled'
        else:
            submit_result['submit_disabled'] = ''

        print("## End FUNCTION student_submit() ##")

        return submit_result

    @XBlock.json_handler
    def fe_parse_question_studio_edits(self, data, suffix=''):
        print("## Start FUNCTION fe_parse_question_studio_edits() ##")
        q = data['question']
        a = data['answer']

        # update fields
        setattr(self, '_question_text', q)
        setattr(self, '_answer_text', a)
        logging.debug("Tammd wants to know q = %s, a = %s", q, a)

        # parse question text
        # template, variables, strings = parse_question_v2(q)
        template, variables, strings = parse_question_improved(q)
        # logging.debug("Tammd wants to know template = {}", template)
        # logging.debug("Tammd wants to know variables = {}", variables)
        # logging.debug("Tammd wants to know strings = {}", strings)

        # parse answer text
        # answer = parse_answer_v2(a, variables)
        answer = parse_answer_improved(a, variables)
        # logging.debug("Tammd wants to know answer = %s", answer)

        # update fields
        setattr(self,'_variables', variables)
        setattr(self,'_question_template', template)
        setattr(self,'_answer_template_string', answer)
        setattr(self,'_string_vars', strings)
        setattr(self, 'show_parser', True)

        print("## End FUNCTION fe_parse_question_studio_edits() ##")

        return {'result': 'success'}

    @XBlock.json_handler
    def fe_submit_studio_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission, two edit modes:

        1. Basic template (Default mode)
        2. Advanced editor

        """

        print("## Start FUNCTION fe_submit_studio_edits() ###")
        # print("data fields: {}".format(data))
        # print("### editor updated xml_data: ###")
        # print(data['raw_editor_xml_data'])

        # print("BEFORE SAVE, self.enable_advanced_editor = {}".format(self.enable_advanced_editor))
        # print("targeted mode, data['enable_advanced_editor'] = {}".format(data['enable_advanced_editor']))
        # print("self.raw_editor_xml_data = {}".format(self.raw_editor_xml_data))

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        string_variables = self._string_vars

        if data['enable_advanced_editor'] == 'False':
            print("### IN CASE self.enable_advanced_editor == False: ###")
            # process problem edit via UI template
            updated_question_template = data['question_template']
            updated_url_image = data['image_url']
            updated_variables = data['variables']
            updated_answer_template = data['answer_template']
            updated_string_vars_list = data['strings']

            # print("updated_string_vars_list = {}".format(updated_string_vars_list))
            # print("BEFORE, self._string_vars = {}".format(self._string_vars))

            string_variables, updated_string_vars, removed_string_vars, added_string_vars = qgb_question_service.update_string_variables(string_variables, updated_string_vars_list)
            # print("updated_string_vars = {}".format(updated_string_vars))
            # print("removed_string_vars = {}".format(removed_string_vars))
            # print("added_string_vars = {}".format(added_string_vars))
            # print("string_variables = {}".format(string_variables))

            # update question template
            updated_question_template = qgb_question_service.update_question_template(updated_question_template,
                                                                            updated_string_vars, removed_string_vars, added_string_vars)

            # # Update XBlock's values
            # self.enable_advanced_editor = False
            # self.question_template_string = updated_question_template
            # self.image_url = updated_url_image
            # self.variables = updated_variables
            # self._answer_template_string = updated_answer_template
            #
            # # setattr(self,'_string_vars', updated_string_vars)
            # setattr(self, '_string_vars', string_variables)
            # setattr(self, '_image_url', updated_url_image)
            # setattr(self, '_question_template', updated_question_template)
            # # setattr(self, '_answer_template', updated_answer_template)
            # setattr(self, '_answer_template_string', updated_answer_template)
            # setattr(self, '_variables', updated_variables)

            # build xml string for problem raw edit fields,
            # then update value to field '_raw_editor_xml_data' for editor
            # input_data = {
            #     'question_template': self.question_template_string,
            #     'image_url': self.image_url,
            #     'variables': self.variables,
            #     'answer_template': self._answer_template_string,
            #     'string_variables': self._string_vars,
            # }
            input_data = {
                'question_template': updated_question_template,
                'image_url': updated_url_image,
                'variables': updated_variables,
                'answer_template': updated_answer_template,
                'string_variables': string_variables,
            }

            # Convert dict data to xml
            xml_string = xml_helper.convert_data_from_dict_to_xml(input_data)

            # Finally, update value for editor field attribute
            setattr(self, '_raw_editor_xml_data', xml_string)

        elif data['enable_advanced_editor'] == 'True':
            print("### IN CASE self.enable_advanced_editor == True: ###")
            # Process raw edit
            updated_xml_string = data['raw_editor_xml_data']

            # Extract data fields from xml string
            raw_edit_data = xml_helper.extract_data_from_xmlstring_to_dict(updated_xml_string)

            # TODO: then save to DB model? To remove this line
            # qgb_db_service.update_question_template(self.xblock_id, updated_question_template, updated_url_image, updated_resolver_selection, updated_variables, updated_answer_template)

            updated_question_template = raw_edit_data['question_template']
            updated_url_image = raw_edit_data['image_url']
            updated_variables = raw_edit_data['variables']
            # get only one firt answer for now.
            # TODO: update to support multi-answers attributes for multiple solutions
            updated_answer_template_dict = raw_edit_data['answer_template'][1]
            string_variables = raw_edit_data['string_variables']

            # convert answer dict to string
            updated_answer_template = xml_helper.convert_answer_template_dict_to_string(updated_answer_template_dict)

            # # "refresh" XBlock's values
            # # update values to global variables
            # self.enable_advanced_editor = True
            # self.question_template_string = updated_question_template
            # self.image_url = updated_url_image
            # self.variables = updated_variables
            # # setattr(self, '_answer_template', updated_answer_template)
            # self._answer_template_string = updated_answer_template
            # # self.resolver_selection = updated_resolver_selection
            #
            # # update values to global fields
            # setattr(self, '_question_template', updated_question_template)
            # setattr(self, '_image_url', updated_url_image)
            # # setattr(self, '_answer_template', updated_answer_template)
            # setattr(self, '_answer_template_string', updated_answer_template)
            # setattr(self, '_variables', updated_variables)
            # setattr(self, '_string_vars', string_variables)

            # update raw edit fields data
            self.raw_editor_xml_data = updated_xml_string
            setattr(self, '_raw_editor_xml_data', updated_xml_string)

        # update fields
        # Update XBlock's values
        self.enable_advanced_editor = False
        self.question_template_string = updated_question_template
        self.image_url = updated_url_image
        self.variables = updated_variables
        self._answer_template_string = updated_answer_template
        setattr(self, '_string_vars', string_variables)
        setattr(self, '_image_url', updated_url_image)
        setattr(self, '_question_template', updated_question_template)
        # setattr(self, '_answer_template', updated_answer_template)
        setattr(self, '_answer_template_string', updated_answer_template)
        setattr(self, '_variables', updated_variables)
        # # update original text
        # setattr(self, '_question_text', self._generated_question)
        # setattr(self, '_answer_text', generated_answer)

        # copy from StudioEditableXBlockMixin (can not call parent method)
        values = {}  # dict of new field values we are updating
        to_reset = []  # list of field names to delete from this XBlock
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            if field_name in data['values']:
                if isinstance(field, JSONField):
                    values[field_name] = field.from_json(data['values'][field_name])
                else:
                    raise JsonHandlerError(400, "Unsupported field type: {}".format(field_name))
            elif field_name in data['defaults'] and field.is_set_on(self):
                to_reset.append(field_name)

        self.clean_studio_edits(values)
        validation = Validation(self.scope_ids.usage_id)

        # We cannot set the fields on self yet, because even if validation fails, studio is going to save any changes we
        # make. So we create a "fake" object that has all the field values we are about to set.
        preview_data = FutureFields(
            new_fields_dict=values,
            newly_removed_fields=to_reset,
            fallback_obj=self
        )

        self.validate_field_data(validation, preview_data)
        # print("preview_data fields: {}".format(preview_data))

        # Generate new problem
        # self._generated_question, self._generated_variables = matlab_question_service.generate_question(
        #     self._question_template, self._variables)
        self._generated_question, self._generated_variables = matlab_question_service.new_problem(
            self._question_template, self._variables, randomization=True)

        # Now, append string_vars into the generated question
        self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
        # generated answer string
        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
                                                                          self._answer_template_string)
        print("## End FUNCTION fe_submit_studio_edits() ###")

        if validation:
            for field_name, value in values.iteritems():
                setattr(self, field_name, value)
            for field_name in to_reset:
                self.fields[field_name].delete_from(self)
            return {'result': 'success'}
        else:
            raise JsonHandlerError(400, validation.to_json())
    

    @XBlock.json_handler
    def show_answer_handler(self, data, suffix=''):
        """
        AJAX handler for "Show/Hide Answer" button
        """
        print("## Start FUNCTION show_answer_handler() ##")
        print("data = {}".format(data))

        self.deserialize_data_from_context(data)

        # generated_answer = matlab_question_service.generate_answer(self._generated_variables, self._answer_template)
        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables, self._answer_template_string)

        print("generated_answer = {}".format(generated_answer))
        print("## END FUNCTION show_answer_handler() ##")

        return {
            'generated_answer': generated_answer
        }

    @XBlock.json_handler
    def get_answer_handler(self, data={}, suffix=''):
        """
        AJAX handler for "Show/Hide Answer" button
        """
        print("## Start FUNCTION get_answer_handler() ##")
        print("data = {}".format(data))

        # self.deserialize_data_from_context(data)

        # print("self._generated_variables = {}".format(self._generated_variables))
        # print("self._answer_template_string = {}".format(self._answer_template_string))
        # generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
        #                                                                   self._answer_template_string)
        #
        # print("generated_answer = {}".format(generated_answer))
        print("self.runtime_generated_variables = {}".format(self.runtime_generated_variables))
        print("self.runtime_generated_variables = {}".format(self.runtime_generated_variables))
        print("self.runtime_generated_answer = {}".format(self.runtime_generated_answer))

        print("## END FUNCTION get_answer_handler() ##")

        return {
            'generated_answer': self.runtime_generated_answer
        }

    @XBlock.json_handler
    def reset_problem_handler(self, data={}, suffix=''):
        """
        AJAX handler for problem reset when invoked 'Reset' button
        """
        print("## Start FUNCTION reset_problem_handler() ##")

        problem = {}
        submit_disabled = ''
        reset_disabled = ''
        show_reset_button = self.allow_reset

        # Reset score and previous submissions made by student
        sub_api.reset_score(self.student_item_key['student_id'], self.student_item_key['course_id'], self.student_item_key['item_id'], clear_state=True)

        # Generate question from template if necessary
        self._generated_question, self._generated_variables = matlab_question_service.new_problem(
            self._question_template, self._variables, randomization=True)
        # Append string variables
        self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
        # Generate answer
        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
                                                                          self._answer_template_string)
        # Update user_state fields
        setattr(self, 'runtime_generated_question', self._generated_question)
        setattr(self, 'runtime_generated_variables', self._generated_variables)
        setattr(self, 'runtime_generated_string_variables', self._string_vars)
        setattr(self, 'runtime_generated_answer', generated_answer)

        # Add following fields to problem variable
        problem['question'] = self.runtime_generated_question
        problem['answer_template'] = self._answer_template_string
        problem['generated_variables'] = json.dumps(self.runtime_generated_variables)
        problem['generated_answer'] = self.runtime_generated_answer
        problem['student_answer'] = self.student_answer
        problem['attempt_number'] = self.attempt_number_string
        problem['point_string'] = self.point_string
        problem['show_reset_button'] = show_reset_button
        problem['reset_disabled'] = reset_disabled
        problem['submit_disabled'] = submit_disabled

        print "self._generated_question = {}".format(self._generated_question)
        print "self.runtime_generated_question = {}".format(self.runtime_generated_question)
        print "self.runtime_generated_answer = {}".format(getattr(self, 'runtime_generated_answer'))
        print "self._generated_variables = {}".format(self._generated_variables)
        print "self.runtime_generated_string_variables = {}".format(self.runtime_generated_string_variables)
        # print "problem = {}".format(problem)
        print "## END FUNCTION reset_problem_handler() ##"

        return problem

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MatlabQuestionTemplateBuilderXBlock",
             """<question_generator_block/>
             """),
            ("Multiple MatlabQuestionTemplateBuilderXBlock",
             """<vertical_demo>
                <question_generator_block/>
                <question_generator_block/>
                <question_generator_block/>
                </vertical_demo>
             """),
        ]
