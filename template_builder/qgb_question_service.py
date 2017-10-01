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


if __name__ == "__main__":
    test3()


