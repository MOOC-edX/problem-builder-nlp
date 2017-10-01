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
from question_parser import parse_question_v2, parse_answer_v2
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
        default = """Given [a] apple and [b] pearl. One apple cost [x] cents, one pearl cost [y] cents.
                  \nCalculate the total price of them?""",
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
                        'min_value': 1,
                        'max_value': 200,
                        'type': 'int',
                        'decimal_places': 0
                    },
                'b':{
                        'name': 'b',
                        'min_value': 1.00,
                        'max_value': 20.99,
                        'type': 'float',
                        'decimal_places': 2
                    }
            },
        scope = Scope.settings
    )

    # Default XML string passed to Advanced Editor's value when create an xBlock
    raw_editor_xml_data = '''
    <problem>
        <description>Given [a] apples and [b] pearls. One apple cost [x] cents, one pearl cost [y] cents.
        \nCalculate the total price of them? </description>
        <images>
            <image_url link="http://example.com/image1">Image</image_url>
        </images>
        <variables>
            <variable name="a" min_value="1" max_value="200" type="integer"/>
            <variable name="b" min_value="1.00" max_value="20.99" type="float" decimal_places="2"/>
        </variables>
        <string_variables>
            <string_variable name="string0" value="str0">
                <value_set name="library1" default="none">Synonym set 1
                    <option>str0</option>
                    <option>str1</option>
                    <option>str2</option>
                    <option>str3</option>
                    <option>str4</option>
                    <option>str5</option>
                </value_set>
                <value_set name="library2">Synonym set 2
                    <option>str0</option>
                    <option>str1</option>
                    <option>str2</option>
                    <option>str3</option>
                    <option>str4</option>
                    <option>str5</option>
                </value_set>
            </string_variable>
            <string_variable name="string1" value="str1">
                <value_set name="library3" default="none">Synonym set 3
                    <option>str0</option>
                    <option>str1</option>
                    <option>str2</option>
                    <option>str3</option>
                    <option>str4</option>
                    <option>str5</option>
                </value_set>
                <value_set name="library4">Synonym set 4
                    <option>str0</option>
                    <option>str1</option>
                    <option>str2</option>
                    <option>str3</option>
                    <option>str4</option>
                    <option>str5</option>
                </value_set>
            </string_variable>
        </string_variables>
        <answer_templates>
            <answer price = "[a] * [x] + [b] * [y]">Teacher's answer</answer>
        </answer_templates>
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
        default="""Given 7 apple and 5 pearl. One apple cost 4 cents, one pearl cost 3 cents.
                    \nCalculate the total price of them?"""
    )

    _answer_text = String (
        scope = Scope.content,
        default = "price = (7 * 4) + (5 * 3)"
    )

    _string_vars = Dict(
        scope=Scope.content,
        default=
        {
            'string0': {
                'name': 'string0',
                'original_text': 'Calculate',
                'default': 'Find',
                'value': 'Find',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 of Calculate",
                            'help': "Synonym set 1",
                            'synonyms': ['Calculate', 'Compute'],
                            'select': 'true',
                        },
                        'context1': {
                            'name': "Context 2 of Calculate (Default)",
                            'help': "Synonym set 2",
                            'synonyms': ['Find', 'Figure out', 'Estimate'],
                            'select': 'false',
                        }
                    }
            },
            'string1': {
                'name': 'string1',
                'original_text': 'apple',
                'default': 'apple',
                'value': 'mango',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 - Fruits",
                            'help': "Synonym set 1",
                            'synonyms': ['apple', 'mango', 'lemon'],
                            'select': 'true',
                        },
                        'context1': {
                            'name': "Context 2 - Computer",
                            'help': "Synonym set 2",
                            'synonyms': ['Apple', 'IBM', 'Google', 'GCS'],
                            'select': 'false',
                        }

                    }
            },
            'string2': {
                'name': 'string2',
                'original_text': 'pearl',
                'default': 'pearl',
                'value': 'pearl',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 - Fruits",
                            'help': "Synonym set 1",
                            'synonyms': ['water melon', 'orange', 'pearl'],
                            'select': 'true',
                        },
                    }
            },
            'string4': {
                'name': 'string4',
                'original_text': 'price',
                'default': 'price',
                'value': 'price',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 of Calculate",
                            'help': "Synonym set 1",
                            'synonyms': ['price', 'cost', 'energy'],
                            'select': 'true',
                        }
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
    is_question_text_parsed = False

    # Default value of original Q & A
    # question_text_origin = "Given a = 5 and b = 10. Calculate the sum, difference of a and b."
    # answer_text_origin = "sum = 15\ndiff = -5"


    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context):
        """
        The primary view of the MatlabQuestionTemplateBuilderXBlock, shown to students when viewing courses.
        """
        print("## Calling FUNCTION student_view() ##")
        print("## START DEBUG INFO ##")
        print("context = {}".format(context))

        context = context

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        should_disbled = ''

        # generate question from template if necessary

        # self._generated_question, self._generated_variables = matlab_question_service.generate_question_old(self._question_template, self._variables)
        self._generated_question, self._generated_variables = matlab_question_service.generate_question(
            self._question_template, self._variables)

        # # first, for each string var, randomly select a value from list of its synonyms
        # # then, update value to this var in the given question template
        # string_variables = self._string_vars
        # for var_name, var in string_variables.iteritems():
        #     value = var['value']
        #     for context_id, context in var['context_list'].iteritems():
        #         if var['context'] == context_id:  # get random value of selected context only
        #             value = qgb_question_service.get_random_item_from_list(context['synonyms'])
        #             # update value for the variable
        #             string_variables[var_name]['value'] = value
        # # update the global variable
        # # setattr(self, '_string_vars', string_variables)

        # append string variables
        self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
        # self._generated_question = qgb_question_service.append_string(self._generated_question, string_variables)
        print("self._generated_question = {}".format(self._generated_question))
        print("self._generated_variables = {}".format(self._generated_variables))

        # load submission data to display the previously submitted result
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        print("previously submitted result = {}".format(submissions))

        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer'] # saved "answer information"
            print("previously submitted answer = {}".format(submissions))

            # INCORRECT ???
            # TODO: remove these
            # self._generated_question = answer['generated_question']
            # self.generated_answer = answer['generated_answer']  # teacher's generated answer
            # self.student_answer = answer['student_answer'] # student's submitted answer

            # TODO: check what is this block for?
            if ('variable_values' in answer): # backward compatibility
                saved_generated_variables = json.loads(answer['variable_values'])
                for var_name, var_value in saved_generated_variables.iteritems():
                    self._generated_variables[var_name] = var_value

            self.attempt_number = latest_submission['attempt_number']
            if (self.attempt_number >= self.max_attempts):
                should_disbled = 'disabled'


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

        frag = Fragment()
        frag.content = loader.render_template('static/html/matlab_question_template_builder/student_view.html', context)
        frag.add_css(self.resource_string("static/css/question_generator_block.css"))
        frag.add_javascript(self.resource_string("static/js/matlab_question_template_builder/student_view.js"))
        frag.initialize_js('MatlabQuestionTemplateBuilderXBlock')

        print("context = {}".format(context))
        print("## End FUNCTION student_view() ##")

        return frag


    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """
        print("## Calling FUNCTION studio_view() ##")
        print("## START DEBUG INFO ##")
        print("context = {}".format(context))

        # if the XBlock has been submitted already then disable the studio_edit screen
        location = self.location.replace(branch=None, version=None)  # Standardize the key in case it isn't already
        item_id=unicode(location)

        print("self._variables = {}".format(self._variables))
        print "self._string_vars = {}".format(self._string_vars)

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

        print("self.is_question_text_parsed = {}".format(self.is_question_text_parsed))

        # self.serialize_data_to_context(context) ??? REMOVE not necessary, remove ???
        context['is_question_text_parsed'] = self.is_question_text_parsed
        context['question_text_origin'] = self._question_text
        context['answer_text_origin'] = self._answer_text

        context['image_url'] = self._image_url
        context['question_template'] = self._question_template
        context['variables'] = self._variables
        context['string_variables'] = self._string_vars
        context['answer_template_string'] = self._answer_template_string
        context['is_submitted'] = 'False'

        # Check default edit mode
        if self.enable_advanced_editor:
            context['current_editor_mode_name'] = ADVANCED_EDITOR_NAME
            context['next_editor_mode_name'] = SIMPLE_EDITOR_NAME
        else:
            context['current_editor_mode_name'] = SIMPLE_EDITOR_NAME
            context['next_editor_mode_name'] = ADVANCED_EDITOR_NAME
        context['enable_advanced_editor'] = self.enable_advanced_editor

        # append xml data for raw xml editor
        context['raw_editor_xml_data'] = self._raw_editor_xml_data

        print("context = {}".format(context))
        print("## End DEBUG INFO ##")

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
        print("## CALLING FUNCTION serialize_data_to_context() ##")

        print("## BEFORE ADDING FIELDS ##")
        print("context = {}".format(context))
        print("## START DEBUG INFO ##")
        print("self._question_template = {}".format(self._question_template))
        print("self._image_url = {}".format(self._image_url))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        # print("self._answer_template= {}".format(self._answer_template))
        print "self._answer_template_string = ", self._answer_template_string


        # Add following fields to context variable
        context['saved_question_template'] = self._question_template
        context['saved_url_image'] = self._image_url
        context['serialized_variables'] = json.dumps(self._variables)
        context['serialized_generated_variables'] = json.dumps(self._generated_variables)
        # context['saved_answer_template'] = self._answer_template  # dict
        context['saved_answer_template'] = self._answer_template_string # string

        # context['saved_resolver_selection'] = self._resolver_selection # Old
        context['saved_resolver_selection'] = self._problem_solver  # use _problem_solver from editable_fields

        print("## AFTER, ADDED FIELDS ##")
        print("context = {}".format(context))
        print("## END DEBUG INFO ##")
        print("## End FUNCTION serialize_data_to_context() ##")


    def deserialize_data_from_context(self, context):
        """
        De-serialize data previously saved to context
        """
        print("## CALLING FUNCTION deserialize_data_from_context() ##")
        print("## START DEBUG INFO ##")

        print("self._question_template = {}".format(self._question_template))
        print("self._image_url = {}".format(self._image_url))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables= {}".format(self._generated_variables))
        # print("self._answer_template= {}".format(self._answer_template))
        print "self._answer_template_string = ", self._answer_template_string

        print("## BEFORE ##")
        print("context = {}".format(context))

        self.question_template_string = context['saved_question_template']
        self.image_url = context['saved_url_image']
        # self._answer_template = context['saved_answer_template']
        self._answer_template_string = context['saved_answer_template']
        #
        self.variables = json.loads(context['serialized_variables'])
        self._generated_variables = json.loads(context['serialized_generated_variables'])
        self.resolver_selection = context['saved_resolver_selection']   # TODO: update this to new field in Settings tab

        print("## GLOBAL VARIABLES, AFTER: ##")
        print("self._question_template = {}".format(self.question_template_string))
        print("self.image_url = {}".format(self.image_url))
        # print("self._answer_template= {}".format(self._answer_template))
        print "self._answer_template_string = ", self._answer_template_string
        print("self.variables = {}".format(self.variables))
        print("self._variables= {}".format(self._variables))
        print("self._generated_variables = {}".format(self._generated_variables))
        print("self.resolver_selection = {}".format(self.resolver_selection))
        print("## End DEBUG INFO ##")
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

        print("## CALLING FUNCTION student_submit() ##")
        print("## START DEBUG INFO ##")
        print("data = {}".format(data))

        self.deserialize_data_from_context(data)

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
    def fe_parse_question_studio_edits(self, data, suffix=''):
        
        q = data['question']
        a = data['answer']
        # update fields
        setattr(self, '_question_text', q)
        setattr(self, '_answer_text', a)
        logging.debug("Tammd wants to know q = %s, a = %s", q, a)

        # parse question text
        template, variables, strings = parse_question_v2(q)
        logging.debug("Tammd wants to know template = {}", template)
        logging.debug("Tammd wants to know variables = {}", variables)
        logging.debug("Tammd wants to know strings = {}", strings)

        # parse answer text
        answer = parse_answer_v2(a, variables)
        logging.debug("Tammd wants to know answer = %s", answer)

        # TODO: use dict for numeric variables so we can remove this conversion for var
        var = {}
        for i in range(len(variables)):
            var['var{}'.format(i)] = variables[i][1]['var{}'.format(i)]

        # update fields
        setattr(self,'_variables', var)
        setattr(self,'_question_template', template)
        setattr(self,'_answer_template_string', answer)
        setattr(self,'_string_vars', strings)

        return {'result': 'success'}

    @XBlock.json_handler
    def fe_submit_studio_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission, two edit modes:

        1. Basic template (Default mode)
        2. Advanced editor

        """

        print("## Calling FUNCTION fe_submit_studio_edits() ###")
        print("## DEBUG INFO ###")
        print("data fields: {}".format(data))
        print("### editor updated xml_data: ###")
        print(data['raw_editor_xml_data'])

        print("BEFORE SAVE, self.enable_advanced_editor = {}".format(self.enable_advanced_editor))
        print("targeted mode, data['enable_advanced_editor'] = {}".format(data['enable_advanced_editor']))

        print("self.raw_editor_xml_data = {}".format(self.raw_editor_xml_data))

        if self.xblock_id is None:
            self.xblock_id = unicode(self.location.replace(branch=None, version=None))

        if data['enable_advanced_editor'] == 'False':
            print("### IN CASE self.enable_advanced_editor == False: ###")
            # process problem edit via UI template
            updated_question_template = data['question_template']
            updated_url_image = data['image_url']
            updated_variables = data['variables']
            updated_answer_template = data['answer_template']
            updated_string_variables = data['strings']
            string_variables = self._string_vars

            print("updated_string_variables = {}".format(updated_string_variables))
            print("TYPE of updated_string_variables = {}".format(type(updated_string_variables)))
            # print("BEFORE, self._string_vars = {}".format(self._string_vars))

            # use list
            # updated_strings = []
            # for string in updated_string_variables:
            #     for i in range(len(string_variables)):
            #         if string_variables[i]['name'] == string['name']:
            #             string_variables[i]['value'] = string['value']
            #             updated_strings.append(string_variables[i])

            # get values of updated string variables
            #
            # use dictionary instead of list
            updated_strings = {}
            for updated_string in updated_string_variables:
                for var_name, string_var in string_variables.iteritems():
                    if string_var['name'] == updated_string['name']:
                        string_var['context'] = updated_string['context']
                        string_var['value'] = updated_string['value']
                        updated_strings[var_name] = string_var

            # print("Data type of updated_strings = {}".format(type(updated_strings)))
            print("updated_strings = {}".format(updated_strings))

            # update string variables
            #
            # new_list = [ string for string in string_variables if string not in updated_strings ]
            # use dictionary
            new_list = {}
            for var_name, string_var in string_variables.iteritems():
                for key, updated_string_var in updated_strings.iteritems():
                    if string_var != updated_string_var:
                        new_list[var_name] = string_var

            updated_question_template  = qgb_question_service.update_default(updated_question_template, new_list)
            logging.debug("Tammd wants to know: %s", updated_string_variables)

            # Update XBlock's values
            self.enable_advanced_editor = False
            self.question_template_string = updated_question_template
            self.image_url = updated_url_image
            self.variables = updated_variables
            self._answer_template_string = updated_answer_template

            setattr(self,'_string_vars', updated_strings)
            setattr(self, '_image_url', updated_url_image)
            setattr(self, '_question_template', updated_question_template)
            # setattr(self, '_answer_template', updated_answer_template)
            setattr(self, '_answer_template_string', updated_answer_template)
            setattr(self, '_variables', updated_variables)

            print("Data type of self._variables = {}".format(type(self._variables)))
            print("AFTER, self._variables = {}".format(self._variables))

            # build xml string for problem raw edit fields,
            # then update value to field '_raw_editor_xml_data' for editor
            input_data = {
                'question_template': self.question_template_string,
                'image_url': self.image_url,
                'variables': self.variables,
                'answer_template': self._answer_template_string
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
            # get only one firt answer for now. TODO: update to support multi-answers attributes for multiple solutions
            updated_answer_template_dict = raw_edit_data['answer_template'][1]
            # updated_resolver_selection = data['problem_solver']

            # convert answer dict to string
            updated_answer_template = xml_helper.convert_answer_template_dict_to_string(updated_answer_template_dict)


            print("BEFORE, self._answer_template_string = ")
            print(self._answer_template_string)

            print("Data type of self._answer_template_string = {}".format(type(self._answer_template_string)))
            print("Data type of updated_answer_template = {}".format(type(updated_answer_template)))

            # "refresh" XBlock's values
            # update values to global variables
            self.enable_advanced_editor = True
            self.question_template_string = updated_question_template
            self.image_url = updated_url_image
            self.variables = updated_variables
            # setattr(self, '_answer_template', updated_answer_template)
            self._answer_template_string = updated_answer_template
            # self.resolver_selection = updated_resolver_selection

            print("AFTER, self._answer_template_string = ")
            print(self._answer_template_string)

            print("Data type of self._answer_template_string = {}".format(type(self._answer_template_string)))

            # update values to global fields
            setattr(self, '_question_template', updated_question_template)
            setattr(self, '_image_url', updated_url_image)
            # setattr(self, '_answer_template', updated_answer_template)
            setattr(self, '_answer_template_string', updated_answer_template)
            setattr(self, '_variables', updated_variables)
            # setattr(self, '_resolver_selection', updated_resolver_selection)

            # update raw edit fields data
            self.raw_editor_xml_data = updated_xml_string
            setattr(self, '_raw_editor_xml_data', updated_xml_string)

        print("AFTER SAVE, self.raw_editor_xml_data = {}".format(self.raw_editor_xml_data))

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
        print("preview_data fields: {}".format(preview_data))

        self._generated_question, self._generated_variables = matlab_question_service.generate_question(
            self._question_template, self._variables)

        # Now, append string_vars into the generated question
        self._generated_question = qgb_question_service.append_string(self._generated_question, self._string_vars)
        # generated answer string
        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables,
                                                                          self._answer_template_string)
        print "generated_answer = ", generated_answer
        print("self._generated_question = {}".format(self._generated_question))
        print("self._generated_variables = {}".format(self._generated_variables))

        setattr(self, '_question_text', self._generated_question)
        setattr(self, '_answer_text', generated_answer)



        print("## End DEBUG INFO ###")

        if validation:
            for field_name, value in values.iteritems():
                setattr(self, field_name, value)
            for field_name in to_reset:
                self.fields[field_name].delete_from(self)
            return {'result': 'success'}
        else:
            raise JsonHandlerError(400, validation.to_json())
    

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


    @XBlock.json_handler
    def show_answer_handler(self, data, suffix=''):
        """
        AJAX handler for "Show/Hide Answer" button
        """
        print("## CALLING FUNCTION show_answer_handler() ##")
        print("## START DEBUG INFO ##")
        print("data = {}".format(data))

        self.deserialize_data_from_context(data)

        # generated_answer = matlab_question_service.generate_answer(self._generated_variables, self._answer_template)
        generated_answer = matlab_question_service.generate_answer_string(self._generated_variables, self._answer_template_string)

        print("generated_answer = {}".format(generated_answer))
        print("## START DEBUG INFO ##")
        print("## END FUNCTION show_answer_handler() ##")

        return {
            'generated_answer': generated_answer
        }


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
