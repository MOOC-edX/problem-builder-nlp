import re
from random import randint, uniform

from decimal import *


ONE_PLACE = Decimal(10) ** -1
TWO_PLACES = Decimal(10) ** -2
THREE_PLACES = Decimal(10) ** -3
FOUR_PLACES = Decimal(10) ** -4
FIVE_PLACES = Decimal(10) ** -5
SIX_PLACES = Decimal(10) ** -6
SEVEN_PLACES = Decimal(10) ** -7

DECIMAL_PLACES = [ ONE_PLACE, TWO_PLACES, THREE_PLACES, FOUR_PLACES, FIVE_PLACES, SIX_PLACES, SEVEN_PLACES ]



def generate_question_template():
    """
    Generates data for a newly created question template
    """
    sample_question_template = "Given a = [a] and b = [b]. Calculate the sum, difference of a and b."
    
    a_variable = {
        'name': 'a',
        'min_value': 0,
        'max_value': 10,
        'type': 'int',
        'decimal_places': 2
    }
    
    b_variable = {
        'name': 'b',
        'min_value': 10,
        'max_value': 20,
        'type': 'int',
        'decimal_places': 2
    }
    
    variables = {
        'a': a_variable,
        'b': b_variable,
    }
    
    sample_answer_template = ""
    
    return sample_question_template, variables, sample_answer_template


def get_decimal_places(var_decimal_places_int):
    if (var_decimal_places_int < 1):
        return ONE_PLACE
    elif (var_decimal_places_int > 7):
        return SEVEN_PLACES
    
    return DECIMAL_PLACES[var_decimal_places_int - 1]


def generate_question(question_template, variables):
    
    compiled_variable_patterns = {}
    generated_variables = {}
    
    
    # generate variables' value
    for var_name, variable in variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile(r'\[' + var_name + r'\]')
        var_type = variable['type']
        var_decimal_places_int = int(variable['decimal_places'])
        
        var_value = ""
        if var_type == 'int':
            var_value = str(randint(int(variable['min_value']), int(variable['max_value'])))
        else: # float
            var_value = str(uniform(float(variable['min_value']), float(variable['max_value'])))
            var_decimal_places = get_decimal_places(var_decimal_places_int)
            var_value = str(Decimal(var_value).quantize(var_decimal_places))

        generated_variables[var_name] = var_value
        
    
    # generate the question and answer
    generated_question = question_template
    for var_name, var_value in generated_variables.iteritems():
        generated_question = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]), generated_question)
    
    
    return generated_question, generated_variables


def generate_answer(generated_variables, answer_template):
    
    compiled_variable_patterns = {}
    for var_name, var_value in generated_variables.iteritems():
        compiled_variable_patterns[var_name] = re.compile('\[' + var_name + '\]')
    
    generated_answer = answer_template
    for var_name, var_value in generated_variables.iteritems():
        generated_answer = compiled_variable_patterns[var_name].sub(str(generated_variables[var_name]), generated_answer)
    
    return generated_answer

def append_string(template, string_variables):
    print("## Calling FUNCTION append_string() ##")
    print("## START DEBUG INFO ##")
    print("template = {}".format(template))
    print("string_variables = {}".format(string_variables))

    # for string in string_variables:
    #     template = re.sub( "\[{}\]".format(string["name"]), "{}".format(string['value']), template )

    # Generate string variables use dict for variables
    # first, for each string var, randomly select a value from list of its synonyms
    # then, update value to this var in the given question template
    for var_name, var in string_variables.iteritems():
        value = var['value']
        print("var_name = {}, value = {}".format(var_name, value))
        for context_id, context in var['context_list'].iteritems():
            if var['context'] == context_id: # get random value of selected context only
                value = get_random_item_from_list(context['synonyms'])
                print("context_id = {}, var_name = {}, value = {}".format(context_id, var_name, value))
                # # update the global variable
                # string_variables[var_name]['value'] = value
        # update template
        template = re.sub( "\[{}\]".format(var["name"]), "{}".format(value), template )

    print("template = {}".format(template))
    print("## End FUNCTION append_string() ##")
    return template

def update_default(template, string_variables):
    print("## Calling FUNCTION update_default() ##")
    print("## START DEBUG INFO ##")
    print("template = {}".format(template))
    print("string_variables = {}".format(string_variables))

    # for string in string_variables:
    #     template = re.sub( "\[{}\]".format(string["name"]), "{}".format(string['default']), template )

    for var_name, var in string_variables.iteritems():
        # template = re.sub( "\[{}\]".format(var["name"]), "{}".format(var['default']), template )
        template = re.sub("\[{}\]".format(var["name"]), "{}".format(var['value']), template)

    print("template = {}".format(template))
    print("## End FUNCTION update_default() ##")
    return template

def update_question_template(template, updated_string_vars={}, removed_string_vars={}, added_string_vars={}):
    print("## Calling FUNCTION update_question_template() ##")
    print("## START DEBUG INFO ##")
    print("template = {}".format(template))
    print("added_string_vars = {}".format(updated_string_vars))
    print("added_string_vars = {}".format(removed_string_vars))

    # for string in added_string_vars:
    #     template = re.sub( "\[{}\]".format(string["name"]), "{}".format(string['default']), template )

    # replace text in the question template by variable name of added string variables
    for var_name, added_string in added_string_vars.iteritems():
        # template = re.sub("\[{}\]".format(added_string["name"]), "{}".format(added_string['value']), template)
        template = re.sub("{}".format(added_string["value"]), "\[{}\]".format(added_string['name']), template)

    # replace variable name the question template by text of removed string variables
    for var_name, removed_string in removed_string_vars.iteritems():
        template = re.sub("{}".format(removed_string["name"]), "\[{}\]".format(removed_string['value']), template)

    print("template = {}".format(template))
    print("## End FUNCTION update_question_template() ##")

    return template

def update_string_variables(string_variables, expected_string_vars_list):
    # canhdq's new method
    updated_string_vars = {}
    added_string_vars = {}
    removed_string_vars = {}
    list_of_current_string_var_name = string_variables.keys()

    # get name list of newly string variables
    list_of_expected_string_var_name = []
    for string in expected_string_vars_list:
        list_of_expected_string_var_name.append(string['name'])
    set_of_expected_string_var_name = set(list_of_expected_string_var_name)
    set_of_current_string_var_name = set(list_of_current_string_var_name)

    # handle updated existing string vars
    for string in expected_string_vars_list:
        var_name = string['name']
        if var_name in list_of_current_string_var_name:
            # Existing string variable
            string_var = string_variables[var_name]
            # Update data for its editable fields
            string_var['context'] = string['context']
            string_var['value'] = string['value']
            string_var['default'] = string['value']
            string_var['original_text'] = string['original_text']
            # then, add this string var into the dict of updated string variables
            updated_string_vars[var_name] = string_var

    # print("Data type of updated_string_vars = {}".format(type(updated_string_vars)))
    print("updated_string_vars = {}".format(updated_string_vars))
    print("removed_string_vars = {}".format(removed_string_vars))
    print("added_string_vars = {}".format(added_string_vars))

    # handle removed/added string vars
    list_of_removed_string_var_name = []
    list_of_updated_string_var_name = []
    for string in list_of_current_string_var_name:
        if string not in set_of_expected_string_var_name:
            list_of_removed_string_var_name.append(string)
        else:
            list_of_updated_string_var_name.append(string)
    # remove string vars
    for var_name in list_of_removed_string_var_name:
        removed_string_vars[var_name] = string_variables[var_name]
        string_variables.pop(var_name)
        # # add string vars
        # list_of_added_string_var_name = [string for string in list_of_expected_string_var_name if
        #                                    string not in set_of_current_string_var_name]
        # for var_name in list_of_added_string_var_name:
        #     added_string_vars[var_name] = {}
        #     string_variables[var_name] = added_string_vars[var_name]

    return string_variables, updated_string_vars, removed_string_vars, added_string_vars

def get_random_item_from_list(list_data):
    '''
    Get a random item from the given list by randomly select an indice from the list

    :param list_data:
    :return: value of item at randomized index of list

    @author: Canh Duong <canhdq@hitachiconsulting.com>
    '''
    max_index = len(list_data) - 1
    random_index = randint(0, max_index)

    return list_data[random_index]

def test1():
    question_template1 = "What is the energy to raise <n> apples to <m> meters?"
    n_variable = {
        'name': 'n',
        'type': 'int',
        'min_value': 1,
        'max_value': 10,
        'decimal_places': 2
    }

    m_variable = {
        'name': 'm',
        'type': 'int',
        'min_value': 5,
        'max_value': 20,
        'decimal_places': 2
    }

    variables = {
        'n': n_variable,
        'm': m_variable
    }

    answer_template = "<n> apples and <m> meters is the answer"

    generated_question, generated_variables = generate_question(question_template1, variables)

    print('test_template1: ' + question_template1)
    print('generated question: ' + generated_question)
    print 'Generated n: ' + generated_variables['n']
    print 'Generated m: ' + generated_variables['m']

    generated_answer = generate_answer(generated_variables, answer_template)
    print('generated answer: ' + generated_answer)

def test2():
    mylist = ['Apple', 'IBM', 'Google', 'GCS']
    print mylist
    item = get_random_item_from_list(mylist)
    print item

def test3():
    template = '''Given 167 [string1] and 3.47 [string2]. One [string1] cost [x] cents, one [string2] cost [y] cents.
[string0] the total price of them?
'''
    string_variables = {
        'string0': {'original_text': 'Calculate', 'name': 'string0', 'default': 'Find', 'value': 'Figure out',
                    'context': 'context0', 'context_list': {
                'context1': {'synonyms': ['Find', 'Figure out', 'Estimate'], 'name': 'Context 2 of Calculate (Default)',
                             'select': 'false', 'help': 'Synonym set 2'},
                'context0': {'synonyms': ['Calculate', 'Compute'], 'name': 'Context 1 of Calculate', 'select': 'true',
                             'help': 'Synonym set 1'}}},
        'string1': {'original_text': 'apple', 'name': 'string1', 'default': 'apple', 'value': 'apple',
                    'context': 'context0',
                    'context_list': {
                            'context1': {'synonyms': ['Apple', 'IBM', 'Google', 'GCS'], 'name': 'Context 2 - Computer',
                                         'select': 'false', 'help': 'Synonym set 2'},
                            'context0': {'synonyms': ['apple', 'mango', 'kool'], 'name': 'Context 1 - Fruits', 'select': 'true',
                                         'help': 'Synonym set 1'}
                        }
                    },
        'string2': {'original_text': 'pearl', 'name': 'string2', 'default': 'pearl', 'value': 'pearl',
                    'context': 'context1',
                    'context_list': {
                        'context1': {'synonyms': ['IBM', 'Google', 'GCS'], 'name': 'Context 2 - Computer',
                                     'select': 'false', 'help': 'Synonym set 2'},
                    }
                    }
    }

    result = append_string(template, string_variables)
    print "generated question = {}".format(result)

def test_update_string_vars():
    data = []
    data['strings'] = [{u'value': u'cost', u'name': u'string2', u'context': u'context0'},
                 {u'value': u'apple', u'name': u'string3', u'context': u'context0'},
                 {u'value': u'pearl', u'name': u'string0', u'context': u'context0'},
                 {u'value': u'price', u'name': u'string1', u'context': u'context0'}]


if __name__ == "__main__":
    test3()


