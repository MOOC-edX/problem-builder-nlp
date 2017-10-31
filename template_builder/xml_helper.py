import sys
from xblock.exceptions import JsonHandlerError, NoSuchViewError

try:
    # Python 3
    import cElementTree as ET
except ImportError:
  try:
    # Python 2 need to import a different module
    import xml.etree.cElementTree as ET
  except ImportError:
    sys.exit("Failed to import cElementTree from any known place")


def convert_data_from_dict_to_xml(data):
    '''
    Convert data fields from dictionary to XML when perform studio submission on Basic Template tab.
    The output will be updated to value of Advanced Editor.

        1. problem description
        2. Image url
        3. variables (name, min_value, max_value, type, decimal_places)
        4. answer_template_string

    :param data -- a dictionary of fields supported for raw editor
    :return:
    <problem>
        <description>Given a = [a] and b = [b]. Calculate the [sum], [difference] of a and b. </description>
        <images>
            <image_url link="http://example.com/image1">Image 1</image_url>
            <image_url link="http://example.com/image2">Image 2</image_url>
        </images>
        <variables>
            <variable name="a" min="1" max="200" type="integer"/>
            <variable name="b" min="1.0" max="20.5" type="float" decimal_places="2"/>
        </variables>
        <answer_templates>
            <answer sum = "[a] + [b]" difference = "[a] - [b]">Teacher's answer</answer>
        </answer_templates>
    </problem>
    '''
    print("## CALLING FUNCTION convert_data_from_dict_to_xml() ##")
    # print("Input data type: {}".format(type(data)))
    print("Input data: {}".format(data))

    xml_string = ''
    # init the root element: problem
    problem = ET.Element('problem')

    # convert question template
    field_question_template = data['question_template']
    description = ET.SubElement(problem, 'description')
    description.text = field_question_template


    # convert image
    field_image_url = data['image_url']
    # xml elements
    images = ET.SubElement(problem, 'images')
    image_url = ET.SubElement(images, 'image_url')
    # Set attribute
    image_url.set('link', field_image_url)

    # convert variables
    field_variables = data['variables']
    # xml elements
    variables_elem = ET.SubElement(problem, 'variables')
    for var_name, attributes in field_variables.iteritems():
        var_name = ET.SubElement(variables_elem, 'variable')
        for attribute, value in attributes.iteritems():
            # Set attribute
            var_name.set(attribute, value)

    # Convert answer template tring to dictionary,
    # then build xml string for raw edit fields
    field_answer_template = data['answer_template']
    # Check for empty input
    if not field_answer_template:
        raise JsonHandlerError(400, "Answer template must not be empty")

    # Parse and convert answer template string to dictionary first
    answer_template_dict = {}
    answer_template_list = field_answer_template.split('\n')

    for answer in answer_template_list:
        # only process if not empty, ignore empty answer template
        if answer:
            # answer template must contains '=' character
            if (answer.find('=') != -1):    # found '=' at lowest index of string
                answer_attrib_list = answer.split('=')
                # print "answer_attrib_list = "
                # print(answer_attrib_list)

                answer_attrib_key = answer_attrib_list[0]
                answer_attrib_value = answer_attrib_list[1]
                # print "answer_attrib_key = "
                # print(answer_attrib_key)
                # print "answer_attrib_value = "
                # print(answer_attrib_value)

                # Remove unexpected white spaces
                answer_attrib_key = answer_attrib_key.lstrip()  # all leading whitespaces are removed from the string.
                answer_attrib_key = answer_attrib_key.rstrip()  # all ending whitespaces are removed from the string.
                answer_attrib_value = answer_attrib_value.lstrip()  # all leading whitespaces are removed from the string.
                answer_attrib_value = answer_attrib_value.rstrip()  # all ending whitespaces are removed from the string.

                # print "REMOVED SPACES, answer_attrib_key = "
                # print(answer_attrib_key)
                # print "REMOVED SPACES,answer_attrib_value = "
                # print(answer_attrib_value)

                # Add answer attribute to dict
                answer_template_dict[answer_attrib_key] = answer_attrib_value
            else:
                raise JsonHandlerError(400, "Unsupported answer format. Answer template must contains '=' character: {}".format(answer))

    # print("Resulted answer_template_dict: {}".format(answer_template_dict))

    # xml elements
    answer_templates = ET.SubElement(problem, 'answer_templates')
    answer = ET.SubElement(answer_templates, 'answer')
    # Add the converted dict data to xml elements
    for attrib_key, attrib_value in answer_template_dict.iteritems():
        answer.set(attrib_key, attrib_value)
        answer.text = "Teacher's answer"

    # Convert string variables dictionary to xml string
    field_string_variables = data['string_variables']
    # xml elements
    string_variables_elem = string_variables_dict_to_xml_element(field_string_variables)
    # Adds the element subelement to the end of this elements internal list of subelements.
    problem.append(string_variables_elem)


    # print "before indent, Problem elem dum = ", ET.dump(problem)
    indented_problem = indent(problem)
    # print "after indent ,Problem elem dum = ", ET.dump(indented_problem)

    xml_string = ET.tostring(indented_problem)

    print "Output xml string = ", xml_string
    print("## End FUNCTION convert_data_from_dict_to_xml() ##")

    return xml_string

def string_variables_dict_to_xml_element(string_variables_dict):
    '''
    Convert string variables dictionary to xml element

    @author: Canh Duong <canhdq@hitachiconsulting.com>

    :param string_variables_dict:
        string_variables_dict = {
            'string0': {
                'name': 'string0',
                'original_text': 'Calculate',
                'default': 'Calculate',
                'value': 'Calculate',
                'context': 'context1',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 of Calculate",
                            'help': "Synonym set 1",
                            'synonyms': ['Calculate', 'Compute'],
                            'select': 'true',
                        },
                        'context1': {
                            'name': "Context 2 of Calculate",
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
                'value': 'apple',
                'context': 'context0',
                'context_list':
                    {
                        'context0': {
                            'name': "Context 1 - Fruits",
                            'help': "Synonym set 1",
                            'synonyms': ['apple', 'mango'],
                            'select': 'true',
                        },
                        'context1': {
                            'name': "Context 2 - Computer",
                            'help': "Synonym set 2",
                            'synonyms': ['Apple', 'IBM', 'Google', 'GCS'],
                            'select': 'false',
                        }

                    }
            }
        }


    :return: string_variables_elem - xml element

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

    '''

    # xml elements
    string_variables_elem = ET.Element('string_variables')
    # Append child
    for var_name, string_var in string_variables_dict.iteritems():
        # create sub-element
        string_variable_elem = ET.SubElement(string_variables_elem, 'string_variable')
        # Set attributes here
        string_variable_elem.set('name', var_name)
        string_variable_elem.set('original_text', string_var['original_text'])
        string_variable_elem.set('value', string_var['value'])
        string_variable_elem.set('default', string_var['default'])
        # create sub-element
        context_list_elem = ET.SubElement(string_variable_elem, 'context_list')
        # Append child
        for context_id, context in string_var['context_list'].iteritems():
            # create sub-element
            context_elem = ET.SubElement(context_list_elem, 'context')
            # Set attributes here
            context_elem.set('name', context['name'])
            # context_elem.text(context['help'])
            if context_id == string_var['context']:
                context_elem.set('select', 'true')
            else:
                context_elem.set('select', 'false')
            # Append child
            for word in context['synonyms']:
                # create sub-element
                option = ET.SubElement(context_elem, 'option')
                # Set text value here
                option.text = word

    return string_variables_elem

def extract_data_from_xmlstring_to_dict(xml_string):
    '''
    Extract raw edit data fields from XML for studio submission on Advanced Editor tab.
    The output will be updated to value of fields Basic Template tab.

        1. problem description
        2. Image url
        3. variables (name, min_value, max_value, type, decimal_places)
        4. answer_template_string

    :param xml_string: string in XML format --

        <problem>
            <description>Given a = [a] and b = [b]. Calculate the sum, difference of a and b. </description>
            <images>
                <image_url link="http://example.com/image1">Image 1</image_url>
            </images>
            <variables>
                <variable name="a" min="1" max="200" type="integer"/>
                <variable name="b" min="1.0" max="20.5" type="float" decimal_places="2"/>
            </variables>
            <answer_templates>
                <answer sum = "[a] + [b]" difference = "[a] - [b]">Teacher's answer</answer>
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
        </problem>

    :return: raw_editor_data_fields -- a dictionary of raw edit supported fields

    '''
    print("## CALLING FUNCTION extract_data_from_xmlstring_to_dict() ##")

    # Reading the xml data from a string:
    # fromstring() parses XML from a string directly into an Element, which is the root element of the parsed tree.
    problem = ET.fromstring(xml_string)
    problem_fields = problem.getchildren()
    # print(problem_fields)

    # init a dict to store problem field values extracted from the xml string
    raw_editor_data_fields = {}

    for field in problem_fields:
        # print("field.tag: " + field.tag)
        # print("field.attrib: ", field.attrib)
        if field.tag == "description":
            # extract the question template
            raw_editor_data_fields["question_template"] = field.text
        elif field.tag == "images":
            # Extract image url
            #
            # A problem can have many images
            # only get first image_url for now
            # TODO: support multiple images
            image_urls = field.findall('image_url')  # find all direct children only for this field.
            # get first image_url
            raw_editor_data_fields["image_url"] = image_urls[0].get('link')  # get its link attrib
        elif field.tag == "variables":
            # Extract variables info
            raw_editor_data_fields["variables"] = {}  # initialize the variables dict
            # find all direct child elements named "variable" under 'variables' element
            variable_list = field.findall("variable")
            for variable in variable_list:
                variable_attributes = variable.attrib
                var_name = variable_attributes["name"]

                # add each variable into the variable dict
                raw_editor_data_fields["variables"][var_name] = variable_attributes
        elif field.tag == "answer_templates":
            # Extract the answers
            raw_editor_data_fields["answer_template"] = {}  # initialize the answers dict
            # find all direct childs named "answer" of element 'answer_templates'
            answer_list = field.findall("answer")
            i = 0
            for answer in answer_list:
                i = i + 1
                answer_attributes = answer.attrib
                # add each answer into the raw_editor_data_fields dict
                raw_editor_data_fields["answer_template"][i] = answer_attributes
        elif field.tag == "string_variables":
            # Extract string variables info
            raw_editor_data_fields["string_variables"] = {}  # initialize the variables dict
            # find all direct child elements named "string_variable" under 'string_variables' element
            string_variable_list = field.findall("string_variable")
            for string_variable in string_variable_list:
                this_string_var = {}
                string_variable_attributes = string_variable.attrib
                var_name = string_variable_attributes["name"]
                this_string_var['name'] = var_name
                this_string_var['original_text'] = string_variable_attributes["original_text"]
                this_string_var['value'] = string_variable_attributes["value"]
                this_string_var['default'] = string_variable_attributes["default"]
                this_string_var['context'] = '' # TBU as following
                this_string_var['context_list'] = {}

                # find all childs elements named "context" under 'string_variable' element
                context_list = string_variable.iter("context")
                i = 0
                for context in context_list:
                    # print "context.tag: {}".format(context.tag)
                    # print "context.attrib: {}".format(context.attrib)
                    context_id = 'context' + str(i)
                    this_string_var['context_list'][context_id] = {}
                    # set attributes

                    this_string_var['context_list'][context_id]['name'] = context.get("name")
                    # this_string_var['context_list'][context_id]['help'] = context.get("help")
                    if context.get("select") == "true": # update selected context for this variable
                        this_string_var['context'] = context_id
                    # synonyms list
                    # find all children option elements
                    option_list = context.findall("option")
                    # synonym_list = [option.text for option in option_list]
                    synonym_list = []
                    for option in option_list:
                        print option.tag
                        print option.text
                        synonym_list.append(option.text)

                    this_string_var['context_list'][context_id]['synonyms'] = synonym_list
                    # print i, context_id
                    # print "synonym_list: {}".format(synonym_list)
                    i = i + 1
                # print "this_string_var: {}".format(this_string_var)

                # add each variable into the variable dict
                raw_editor_data_fields["string_variables"][var_name] = this_string_var

    print("## End FUNCTION extract_data_from_xmlstring_to_dict() ##")

    return raw_editor_data_fields

def convert_answer_template_dict_to_string(dict, sep ='\n'):

    result = ""
    for key, value in dict.iteritems():
        result = result + key + '=' + value
        result = result + sep

    return result

# TODO: check why this function has problem? Only return the last child tag of elem.
# in-place prettyprint formatter
# def indent(elem, level=0):
#     i = "\n" + level*"  "
#     if len(elem):
#         if not elem.text or not elem.text.strip():
#             elem.text = i + "  "
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = i
#         for elem in elem:
#             indent(elem, level+1)
#         if not elem.tail or not elem.tail.strip():
#             elem.tail = i
#     else:
#         if level and (not elem.tail or not elem.tail.strip()):
#             elem.tail = i
#     return elem

# Follow https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

def test_string_variables_dict_to_xml_element(string_variables_dict):
    elem = string_variables_dict_to_xml_element(string_variables_dict)
    xml_string = ET.tostring(indent(elem))
    print xml_string


if __name__ == '__main__':
    string_variables_dict = {
        'string0': {
            'name': 'string0',
            'original_text': 'Calculate',
            'default': 'Calculate',
            'value': 'Calculate',
            'context': 'context1',
            'context_list':
                {
                    'context0': {
                        'name': "Context 1 of Calculate",
                        'help': "Synonym set 1",
                        'synonyms': ['Calculate', 'Compute'],
                        'select': 'true',
                    },
                    'context1': {
                        'name': "Context 2 of Calculate",
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
            'value': 'apple',
            'context': 'context0',
            'context_list':
                {
                    'context0': {
                        'name': "Context 1 - Fruits",
                        'help': "Synonym set 1",
                        'synonyms': ['apple', 'mango'],
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
                        'synonyms': ['cherry', 'ivory', 'pearl'],
                        'select': 'true',
                    },
                    'context1': {
                        'name': "Context 2 - Computer",
                        'help': "Synonym set 2",
                        'synonyms': ['Apple', 'IBM', 'Google', 'GCS'],
                        'select': 'false',
                    }

                }
        }
    }

    xml_string_vars = '''
    <string_variables>
        <string_variable name="string0" original_text="Calculate" value="str0" default="Calculate" >
		    <context_list>
                <context name="Context 1" select="true">Synonym set 1
                    <option>1_str0</option>
                    <option>1_str1</option>
                    <option>1_str2</option>
                    <option>1_str3</option>
                    <option>1_str4</option>
                    <option>1_str5</option>
                </context>
                <context name="Context 2" select="false">Synonym set 2
                    <option>2_str0</option>
                    <option>2_str1</option>
                    <option>2_str2</option>
                    <option>2_str3</option>
                    <option>2_str4</option>
                    <option>2_str5</option>
                </context>
		    </context_list>
        </string_variable>

        <string_variable name="string1" original_text="apple" value="apple" default="apple" >
		    <context_list>
                <context name="Context 3" select="true">Synonym set 3
                    <option>3_str0</option>
                    <option>3_str1</option>
                    <option>3_str2</option>
                    <option>3_str3</option>
                    <option>3_str4</option>
                    <option>3_str5</option>
                </context>
                <context name="Context 4" select="false">Synonym set 4
                    <option>4_str0</option>
                    <option>4_str1</option>
                    <option>4_str2</option>
                    <option>4_str3</option>
                    <option>4_str4</option>
                    <option>4_str5</option>
                </context>
		    </context_list>
        </string_variable>

        <string_variable name="string2" original_text="pearl" value="pearl" default="pearl" >
		    <context_list>
                <context name="Context 5" select="true">Synonym set 5
                    <option>5_str0</option>
                    <option>5_str1</option>
                    <option>5_str2</option>
                    <option>5_str3</option>
                    <option>5_str4</option>
                    <option>5_str5</option>
                </context>
                <context name="Context 6" select="false">Synonym set 6
                    <option>6_str0</option>
                    <option>6_str1</option>
                    <option>6_str2</option>
                    <option>6_str3</option>
                    <option>6_str4</option>
                    <option>6_str5</option>
                </context>
		    </context_list>
        </string_variable>
    </string_variables>
    '''

    xml_problem = '''
    <problem>
  <description>Given [var1] [string0] and [var3] [string5] One [string0] cost [var2] cents , one [string3] cost [var0] [string2] Calculate the total [string1] of them ?</description>
<images>
    <image_url link="" />
  </images>
<variables>
    <variable decimal_places="2" max_value="100" min_value="1" name="var1" type="int" />
  <variable decimal_places="2" max_value="100" min_value="1" name="var0" type="int" />
  <variable decimal_places="2" max_value="5" min_value="1" name="var3" type="float" />
  <variable decimal_places="2" max_value="7" min_value="3" name="var2" type="float" />
  </variables>
<answer_templates>
    <answer price="( [var1] * [var2] ) + ( [var3] * [var0] )">Teacher's answer</answer>
  </answer_templates>
<string_variables>
    <string_variable default="pearl." name="string5" original_text="pearl." value="pearl.">
      <context_list>
        <context name="Synonyms of pearl." select="true">
          <option>pearl.</option>
        </context>
      </context_list>
    </string_variable>
  <string_variable default="cents." name="string2" original_text="cents." value="cents.">
      <context_list>
        <context name="Synonyms of cents." select="true">
          <option>cents.</option>
        </context>
      </context_list>
    </string_variable>
  <string_variable default="pearl" name="string3" original_text="pearl" value="pearl">
      <context_list>
        <context name="Synonyms of pearl" select="true">
          <option>ivory</option>
        <option>drop</option>
        <option>off-white</option>
        <option>pearl</option>
        <option>bead</option>
        <option>bone</option>
        </context>
      </context_list>
    </string_variable>
  <string_variable default="apple" name="string0" original_text="apple" value="apple">
      <context_list>
        <context name="Synonyms of apple" select="true">
            <option>orchard_apple_tree</option>
            <option>apple</option>
            <option>Malus_pumila</option>
        </context>
      </context_list>
    </string_variable>
  <string_variable default="price" name="string1" original_text="price" value="price">
      <context_list>
        <context name="Synonyms of price" select="true">
            <option>terms</option>
            <option>price</option>
            <option>damage</option>
            <option>cost</option>
            <option>monetary_value</option>
            <option>toll</option>
            <option>Leontyne_Price</option>
            <option>Price</option>
            <option>Mary_Leontyne_Price</option>
        </context>
      </context_list>
    </string_variable>
  </string_variables>
</problem>
    '''

    # test_string_variables_dict_to_xml_element(string_variables_dict)
    proplem_dict = extract_data_from_xmlstring_to_dict(xml_problem)
    print proplem_dict
