import re
# from random import randint, uniform
import random

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
            var_value = str(random.randint(int(variable['min_value']), int(variable['max_value'])))
        else: # float
            var_value = str(random.uniform(float(variable['min_value']), float(variable['max_value'])))
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
    print("## Start FUNCTION append_string() ##")
    print("template = {}".format(template))
    print("string_variables = {}".format(string_variables))

    # for string in string_variables:
    #     template = re.sub( "\[{}\]".format(string["name"]), "{}".format(string['value']), template )

    # Generate string variables use dict for variables
    # first, for each string var, randomly select a value from list of its synonyms
    # then, update value to this var in the given question template
    for var_name, var in string_variables.iteritems():
        value = var['value']
        # print("var_name = {}, value = {}".format(var_name, value))
        for context_id, context in var['context_list'].iteritems():
            if var['context'] == context_id: # get random value of selected context only
                value = get_random_item_from_list(context['synonyms'])
                # print("context_id = {}, var_name = {}, value = {}".format(context_id, var_name, value))
        # update template
        template = re.sub( "\[{}\]".format(var["name"]), "{}".format(value), template )

    print("template = {}".format(template))
    print("## End FUNCTION append_string() ##")
    return template

def update_default(template, string_variables):
    print("## Start FUNCTION update_default() ##")
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
    print("## Start FUNCTION update_question_template() ##")
    print("input template = {}".format(template))
    # print("added_string_vars = {}".format(updated_string_vars))
    # print("removed_string_vars = {}".format(removed_string_vars))

    # For added string variables, replace text in the question template by variable name
    for var_name, added_var in added_string_vars.iteritems():
        template = re.sub("{}".format(added_var["value"]), "\[{}\]".format(added_var['name']), template)

    # For removed string variables, replace variable name in the question template by its original text
    for var_name, removed_var in removed_string_vars.iteritems():
        template = re.sub("\[{}\]".format(removed_var["name"]), "{}".format(removed_var['original_text']), template)

    print("output template = {}".format(template))
    print("## End FUNCTION update_question_template() ##")

    return template

def update_string_variables(string_variables, expected_string_vars_list):
    # canhdq's new method
    updated_string_vars = {}
    added_string_vars = {}
    removed_string_vars = {}
    list_of_current_string_var_name = string_variables.keys()

    # get list of all string var name of submitted string variables
    list_of_expected_string_var_name = []
    for string in expected_string_vars_list:
        list_of_expected_string_var_name.append(string['name'])
    set_of_expected_string_var_name = set(list_of_expected_string_var_name)
    set_of_current_string_var_name = set(list_of_current_string_var_name)

    # handle updated existing string vars
    for string in expected_string_vars_list:
        var_name = string['name']
        if var_name in set_of_current_string_var_name:  # use set for better performance
            # Existing string variable
            string_var = string_variables[var_name]
            # Update data for its editable fields
            string_var['context'] = string['context']
            string_var['value'] = string['value']
            string_var['default'] = string['value']
            # then, add this string var into the dict of updated string variables
            updated_string_vars[var_name] = string_var
    # update changes in updated_string_vars to current string_variables
    string_variables.update(updated_string_vars)

    # handle removed/added string vars
    list_of_removed_string_var_name = []
    list_of_updated_string_var_name = []
    for string in list_of_current_string_var_name:
        if string not in set_of_expected_string_var_name:   # use set for better performance
            list_of_removed_string_var_name.append(string)
        else:
            list_of_updated_string_var_name.append(string)
    # remove string vars
    for var_name in list_of_removed_string_var_name:
        removed_string_vars[var_name] = string_variables[var_name]
        string_variables.pop(var_name)
    # # add string vars
    # # TODO: handle add string vars from tab Basic Template
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
    random_index = random.randint(0, max_index)

    return list_data[random_index]

def test_select_random_items():
    mylist = ['Apple', 'IBM', 'Google', 'GCS']
    print mylist
    # item = get_random_item_from_list(mylist)
    # print item
    # best_preserve(mylist)
    # use random.sample
    items = random.sample(mylist, 2)
    print items


def test_append_string_vars_to_template():
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

def test_update_question_template():
    template = '''Given [var1] [string0] and [var3] [string5] One [string0] [string4] [var2] cents, one [string3] [string4] [var0] [string2]
                [string6] the total[string1] of them ?'''

    expected_string_vars_list = [{u'value': u'cost', u'name': u'string4', u'context': u'context0'},
                                 {u'value': u'pearl', u'name': u'string3', u'context': u'context0'},
                                 {u'value': u'apple', u'name': u'string0', u'context': u'context0'},
                                 {u'value': u'price', u'name': u'string1', u'context': u'context0'}]

    updated_string_vars = {
        u'string4': {u'original_text': u'cost', u'name': u'string4', u'default': u'cost', u'value': u'cost',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'be', u'price', u'cost', u'monetary_value', u'toll'],
                              u'name': u'Synonyms of cost', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'cost'"}}},
        u'string3': {u'original_text': u'pearl', u'name': u'string3', u'default': u'pearl', u'value': u'pearl',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'ivory', u'drop', u'off-white', u'pearl', u'bead', u'bone'],
                              u'name': u'Synonyms of pearl', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'pearl'"}}},
        u'string0': {u'original_text': u'apple', u'name': u'string0', u'default': u'apple', u'value': u'apple',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'orchard_apple_tree', u'apple', u'Malus_pumila'],
                              u'name': u'Synonyms of apple', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'apple'"}}},
        u'string1': {u'original_text': u'price', u'name': u'string1', u'default': u'price', u'value': u'price',
                     u'context': u'context0', u'context_list': {u'context0': {
                u'synonyms': [u'terms', u'price', u'damage', u'cost', u'monetary_value', u'toll', u'Leontyne_Price',
                              u'Price', u'Mary_Leontyne_Price'], u'name': u'Synonyms of price', u'select': u'true',
                u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'price'"}}}}

    added_string_vars = {
        u'string4': {u'original_text': u'cost', u'name': u'string4', u'default': u'cost', u'value': u'cost',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'be', u'price', u'cost', u'monetary_value', u'toll'],
                              u'name': u'Synonyms of cost', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'cost'"}}},
        u'string3': {u'original_text': u'pearl', u'name': u'string3', u'default': u'pearl', u'value': u'pearl',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'ivory', u'drop', u'off-white', u'pearl', u'bead', u'bone'],
                              u'name': u'Synonyms of pearl', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'pearl'"}}},
        u'string0': {u'original_text': u'apple', u'name': u'string0', u'default': u'apple', u'value': u'apple',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'orchard_apple_tree', u'apple', u'Malus_pumila'],
                              u'name': u'Synonyms of apple', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'apple'"}}},
        u'string1': {u'original_text': u'price', u'name': u'string1', u'default': u'price', u'value': u'price',
                     u'context': u'context0', u'context_list': {u'context0': {
                u'synonyms': [u'terms', u'price', u'damage', u'cost', u'monetary_value', u'toll', u'Leontyne_Price',
                              u'Price', u'Mary_Leontyne_Price'], u'name': u'Synonyms of price', u'select': u'true',
                u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'price'"}}}}

    removed_string_vars = {
        u'string6': {u'original_text': u'Calculate', u'name': u'string6', u'default': u'Calculate',
                     u'value': u'Calculate', u'context': u'context0', u'context_list': {u'context0': {
                u'synonyms': [u'count', u'account', u'cypher', u'compute', u'Calculate', u'work_out', u'look',
                              u'reckon', u'direct', u'depend', u'forecast', u'aim', u'cipher', u'figure', u'estimate',
                              u'count_on', u'bet', u'calculate'], u'name': u'Synonyms of Calculate', u'select': u'true',
                u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'Calculate'"}}
                     },
        u'string5': {u'original_text': u'pearl.', u'name': u'string5', u'default': u'pearl.', u'value': u'pearl.',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'pearl.'], u'name': u'Synonyms of pearl.', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'pearl.'"}}
                     },
        u'string2': {u'original_text': u'cents.', u'name': u'string2', u'default': u'cents.', u'value': u'cents.',
                     u'context': u'context0', u'context_list': {
                u'context0': {u'synonyms': [u'cents.'], u'name': u'Synonyms of cents.', u'select': u'true',
                              u'help': u"Pure list of words (NN and NNP) generated by NLTK from the original text 'cents.'"}}
                     }}

    update_question_template(template, updated_string_vars, removed_string_vars, added_string_vars)

if __name__ == "__main__":
    # test_update_question_template()
    test_select_random_items()

