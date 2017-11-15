import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, JSONField, Integer, String, Boolean, Dict
from xblock.fragment import Fragment

from xblock.exceptions import JsonHandlerError, NoSuchViewError
from xblock.validation import Validation

from submissions import api as sub_api
from sub_api_util import SubmittingXBlockMixin

from xblockutils.studio_editable import StudioEditableXBlockMixin, FutureFields
from xblockutils.resources import ResourceLoader

import matlab_service
import qgb_question_service
import json
from resolver_machine import resolver_machine
import logging
log =logging.getLogger(__name__)
from .models import MatlabQuestion, QuestionNode
# import xblock_deletion_handler

loader = ResourceLoader(__name__)
def _(text):
    return text
@XBlock.needs("i18n")
class MatlabExerciseGeneratorXBlock(XBlock, SubmittingXBlockMixin, StudioEditableXBlockMixin):
    """
    Question Generator XBlock
    """
    CATEGORY ='tb-matlab-question'
    STUDIO_LABEL = _(u'Matlab Question Generator')
    display_name = String(
        display_name="Question Generator XBlock",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Question Generator XBlock"
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

    resolver_selection = Integer(
        display_name = "Resolver Selection",
        default = 0,
        help = "Please choose Matlab if you want to auto grading the matlab exercise",
        values=(
                {"display_name": "None", "value": 0},
                {"display_name": "Matlab", "value": 1},
            )
        )
    student_answer = String (
        display_name = "Student Answer Box",
        default = "",
        scope = Scope.user_state
        )

    question_template = "Given a =[a] and b = [b]. Calculate the [string0] of a and b."
    variables =  {
                'a': {'name': 'a',
                'min_value': 0,
                'max_value': 10,
                'type': 'int',
                'decimal_places': 2
                } ,
                'b' :{'name': 'b',
                'min_value': 10,
                'max_value': 20,
                'type': 'int',
                'decimal_places': 2
                }
            }
    answer_template = "x =[a] + [b]"
    editable_fields = ('display_name', 'max_attempts', 'max_points', 'show_points_earned',
                       'show_submission_times', 'show_answer','resolver_selection')
    image_url = ""
    resolver_handling = resolver_machine()
    has_score = True
    matlab_server_url = resolver_handling.getDefaultAddress()
    matlab_solver_url = resolver_handling.getDefaultURL()
    attempt_number = 0
    var0 = {
        "name" : "string0",
        "default" : "sum",
        "example" : "sum",
        "synonyms" : ["sum", "difference"]
    }
    string_variables = []
    string_variables.append(var0)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_models_object(self):
        models = None
        try:
            models = QuestionNode.objects.get(block_id = self.scope_ids.usage_id)
            log.error("This block {%s} have been created ", self.scope_ids.usage_id)
        except QuestionNode.DoesNotExist:
            models = QuestionNode.objects.get(block_id=self.parent)
            models.pk = None
            models.pre_block_id = self.parent
            models.block_id = self.scope_ids.usage_id
            parent_upper_1 = self.runtime.get_block(self.parent)
            parent_upper_2 = self.runtime.get_block(parent_upper_1.parent)
            parent_upper_3 = self.runtime.get_block(parent_upper_2.parent)
            models.outermost_block_id = parent_upper_3.scope_ids.usage_id
            log.error("This matlab question block {%s} have been created:" , models.outermost_block_id)
            models.save()
        models = QuestionNode.objects.get(block_id = self.scope_ids.usage_id)
        matlab_models = None
        try:
            matlab_models = MatlabQuestion.objects.get(block_id = self.scope_ids.usage_id)
            log.error("This matlab question block {%s} have been created:" , self.scope_ids.usage_id)
        except MatlabQuestion.DoesNotExist:
            obj = MatlabQuestion.objects.create(block_id = self.scope_ids.usage_id)
            matlab_models = MatlabQuestion.objects.get(block_id = self.scope_ids.usage_id)
            matlab_models.question_template = models.parsed_question
            matlab_models.answer_template = models.parsed_answer
            matlab_models.variables = models.parsed_number_variables
            matlab_models.save()
        return models, matlab_models

    def student_view(self, context):
        """
        The primary view of the QuestionGeneratorXBlock, shown to students when viewing courses.
        """

        should_disbled = ''
        models, matlab_models = self.get_models_object()

        variables = {}
        question_template = ""
        string_variables = []
        if matlab_models.question_template is None:
            question_template = self.question_template
        else:
            question_template = matlab_models.question_template

        if matlab_models.variables is None:
            variables = self.variables
        else:
            variable_dict = json.loads(matlab_models.variables)
            for variable in variable_dict:
                variables[variable[1]['var']] = variable[1]['shadow'][variable[1]['var']]
            logging.error("Tammd wants to know generated variables %s", variables)
        if models.parsed_string_variables is None:
            string_variables = self.string_variables
        else:
            string_variables = json.loads(models.parsed_string_variables)
        # generate question from template if necessary
        matlab_models.generated_question, generated_variables = qgb_question_service.generate_question(question_template, variables)
        matlab_models.generated_question = qgb_question_service.append_string(matlab_models.generated_question, string_variables)
        logging.error("Tammd wants to know generated_question %s , generated_variables %s", matlab_models.generated_question, generated_variables)
        logging.error("Tammd wants to know string_variables: %s", string_variables)

        matlab_models.generated_variable = json.dumps(generated_variables)
        # load submission data to display the previously submitted result
        submissions = sub_api.get_submissions(self.student_item_key, 1)
        if submissions:
            latest_submission = submissions[0]

            # parse the answer
            answer = latest_submission['answer']  # saved "answer information"
            self.student_answer = answer['student_answer']  # student's submitted answer

            self.attempt_number = latest_submission['attempt_number']
            if (self.attempt_number >= self.max_attempts):
                should_disbled = 'disabled'
        #else:
            # save the submission
        #    submission_data = {
        #        'student_answer': "",

         #   }
         #   submission = sub_api.create_submission(self.student_item_key, submission_data)
         #   sub_api.set_score(submission['uuid'], 0, self.max_points)

        context['disabled'] = should_disbled
        context['student_answer'] = self.student_answer
        context['image_url'] = self.image_url
        context['attempt_number'] = self.attempt_number_string
        context['point_string'] = self.point_string
        context['question'] = matlab_models.generated_question
        context['show_answer'] = self.show_answer

        frag = Fragment()
        frag.content = loader.render_template('static/html/matlab_generator_xblock.html', context)
        frag.add_css(self.resource_string("static/css/question_generator_block.css"))
        frag.add_javascript(self.resource_string("static/js/src/matlab_generator_xblock.js"))
        frag.initialize_js('QuestionGeneratorXBlock')
        matlab_models.save()
        models.save()
        return frag

    def studio_view(self, context):
        """
        Render a form for editing this XBlock (override the StudioEditableXBlockMixin's method)
        """


        # Student not yet submit then we can edit the XBlock
        fragment = Fragment()
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

        models, matlab_models = self.get_models_object()
        if matlab_models.image_url is None:
            context['image_urls'] = ""
        else:
            context['image_url'] =matlab_models.image_url
        if matlab_models.question_template is None:
            context['question_template'] = self.question_template
        else:
            context['question_template'] = matlab_models.question_template
        if matlab_models.variables is None:
            context['variables'] = self.variables
        else:
            variables = {}
            variable_dict = json.loads(matlab_models.variables)
            for variable in variable_dict:
                variables[variable[1]['var']] = variable[1]['shadow'][variable[1]['var']]
            context["variables"] = variables
        if matlab_models.answer_template is None:
            context['answer_template'] = self.answer_template
        else:
            context['answer_template'] = matlab_models.answer_template
        context['is_submitted'] = 'False'
        if models.parsed_string_variables is None:

            context['string_variables'] = self.string_variables
        else:
            context['string_variables'] = json.loads(models.parsed_string_variables)
            

        fragment.content = loader.render_template('static/html/matlab_generator_studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/question_generator_block_studio_edit.css"))
        fragment.add_javascript(loader.load_unicode('static/js/src/matlab_generator_studio_edit.js'))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment

    @XBlock.json_handler
    def student_submit(self, data, suffix=''):
        """
        AJAX handler for Submit button
        """
        models, matlab_models = self.get_models_object()
        generated_variables = json.loads(matlab_models.generated_variable)

        points_earned = 0

        # TODO generate the teacher's answer

        self.student_answer = data['student_answer']

        # save the submission
        submission_data = {
            'student_answer': self.student_answer,

        }
        generated_answer = qgb_question_service.generate_answer(generated_variables, self.answer_template)
        matlab_models.generated_answer = generated_answer
        matlab_models.save()

        # call matlab
        evaluation_result = self.resolver_handling.syncCall(self.resolver_selection, generated_answer, self.student_answer)

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

        return submit_result

    @XBlock.json_handler
    def fe_submit_studio_edits(self, data, suffix=''):
        """
        AJAX handler for studio edit submission
        """

        models, matlab_models = self.get_models_object()
        matlab_models.question_template = data['question_template']
        matlab_models.answer_template = data['answer_template']
        matlab_models.image_url = data['image_url']
        #matlab_models.variables = json.dumps(data['variables'])
        update_variables = []
        variables = json.loads(matlab_models.variables)
        for k,v in data['variables'].iteritems() :
            found = False
            for i in range(len(variables)):
                if k == variables[i][1]['var']:
                    variables[i][1]['shadow'][variables[i][1]['var']] = v
                    found = True
                if found == True:
                    update_variables.append(variables[i])
                    break
                else:
                    temp2 = {}
                    temp1 = None
                    if v['type'] == 'int':
                        temp1 = 1
                        temp2['type'] = 'int'
                    else:
                        temp1 = 3.14
                        temp2['type'] = 'float'
                    temp2['var'] = k
                    temp2['shadow'] = {
                        k : v
                    }
                    update_variables.append((temp1,temp2))
                    break
                        
        matlab_models.variables = json.dumps(update_variables)
        string_variables = json.loads(models.parsed_string_variables)
        update_strings = []
        for string in data['strings']:
            for i in range(len(string_variables)):
                if string_variables[i]['name'] == string['name']:
                    string_variables[i]['example'] = string['example']
                    update_strings.append(string_variables[i])
    
        new_list = [ string for string in string_variables if string not in update_strings ]
         
        matlab_models.question_template = qgb_question_service.update_default(matlab_models.question_template, new_list)

        logging.error("Tammd wants to know strings %s %", data['strings'], update_strings)
        matlab_models.save()
        models.parsed_string_variables = json.dumps(update_strings)
        models.save()
        # call parent method
        # StudioEditableXBlockMixin.submit_studio_edits(self, data, suffix)
        # self.submit_studio_edits(data, suffix)
        # super(FormulaExerciseXBlock, self).submit_studio_edits(data, suffix)

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

        models, matlab_models = self.get_models_object()
        generated_variable = json.loads(matlab_models.generated_variable)
        answer_template = ""
        if matlab_models.answer_template is None:
            answer_template = self.answer_template
        else:
            answer_template = matlab_models.answer_template
        generated_answer = qgb_question_service.generate_answer(generated_variable, answer_template)
        matlab_models.generated_answer = generated_answer
        matlab_models.save()

        log.error("Tammd wants to know generated_anser: %s, generated_variables : %s, answer_template : %s", generated_answer, str(generated_variable), self.answer_template)
        return {
            'generated_answer': generated_answer
        }

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("QuestionGeneratorXBlock",
             """<question_generator_block/>
             """),
            ("Multiple QuestionGeneratorXBlock",
             """<vertical_demo>
                <question_generator_block/>
                <question_generator_block/>
                <question_generator_block/>
                </vertical_demo>
             """),
        ]
