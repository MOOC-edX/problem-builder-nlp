from nltk import word_tokenize
from nltk import pos_tag
import re
ANSWER_SEPERATOR = "Answer"

def tokenization(sentences):
	words = word_tokenize(sentences)
	return words

def omit_stop_word(list_of_string):
    	from nltk.corpus import stopwords
    	stop_words = set(stopwords.words('english'))
    	return [s for s in list_of_string if s not in stop_words]

def is_numerical(tag):
    	return tag == 'CD'


# Simple way to tagging the single word 
def part_of_speech_tagging(list_of_string):
    	return [t for t in pos_tag(list_of_string)]


def parse_noun(sentences):
    words = tokenization(sentences)
    list_pos = part_of_speech_tagging(words)
    import string
    punctuations = list(string.punctuation)
    allNoun = [word for word, tag in list_pos if tag in ['NN', 'NNP'] and word not in punctuations ]
    allNoun = set(allNoun)     
    allNoun = list(allNoun)
    import nltk
    from nltk.corpus import wordnet
    list_dict = []
    for i in range(len(allNoun)):
        synonyms = []
        for syn in wordnet.synsets(allNoun[i]):
            for l in syn.lemmas:
                synonyms.append(l.name)
        list_dict.append (
            {
                "name" : "string{}".format(i),
                "default" : allNoun[i],
                "example" : allNoun[i],
                "synonyms" : list(set([allNoun[i]] + synonyms) )
            }
        )
        #print list_dict[i]
    return list_dict
def parse_answer(answer, variables):
    words = tokenization(answer)
    answer_template = ""
    for variable in variables:
        for i in range(len(words)):
            if words[i] == variable[0]:
                words[i] = '[{}]'.format(variable[1]['var'])
    answer_template = ' '.join(words)
    return answer_template

def parse_answer_v2(answer, variables):
    words = tokenization(answer)
    answer_template = ""
    for i in range(len(variables)):
        for j in range(len(words)):
            if words[j] == variables[i][0]:
                words[j] = '[{}]'.format(variables[i][1]['var{}'.format(i)]['name'])
    answer_template = ' '.join(words)
    return answer_template

def parse_question_v2(sentences):
    words = tokenization(sentences)
    list_pos = part_of_speech_tagging(words)
    variables = []
    for word in list_pos:
        try:
            if is_numerical(word[1]) and isinstance(int(word[0]),int):
                variables.append((word[0],'int'))
        except ValueError:
            print "oops !! There is a string or float in the list"
            try:
                if isinstance(float(word[0]), float):
                    variables.append( (word[0],'float') )
            except ValueError:
                print "oops: the last call this is the string"
    variables = list(set(variables))
    variable_names =  []
    for i in range(len(variables)):
        variable_names.append( (variables[i][0],
            {
                'var{}'.format(i) :
                {
                    'name' : 'var{}'.format(i) ,
                    'min_value' : 1,
                    'max_value' : 100,
                    'type' : variables[i][1],
                    'decimal_places' : 2
                }
            })
        )
    string_variables = parse_noun(sentences)
    template = ""
    for i in range(len(variable_names)):
        for j in range(len(words)):
            if words[j] == variable_names[i][0]:
                words[j] = '[{}]'.format( variable_names[i][1]['var{}'.format(i)]['name'] )
    template = ' '.join(words)
    for variable in string_variables:
         template = re.sub( " {} ".format(variable["default"]) , " [{}] ".format(variable["name"]), template )
    return template, variable_names, string_variables


def parse_question(sentences):

    words = tokenization(sentences)
    list_pos = part_of_speech_tagging(words)
    variables = []
    for word in list_pos:
        try:
            if is_numerical(word[1]) and isinstance(int(word[0]),int):
                variables.append((word[0],'int'))
        except ValueError:
            print "oops !! There is a string or float in the list"
            try:
                if isinstance(float(word[0]), float):
                    variables.append((word[0],'float'))
            except ValueError:
                print "oops: the last call this is the string"
    variables = list(set(variables))
    variable_names =  []
    for i in range(len(variables)):
        variable_names.append((variables[i][0],
            {
                'var'   : 'var{}'.format(i),
                'type'   : variables[i][1],
                'shadow' :
                {
                    'var{}'.format(i) : 
                    {   'name' : 'var{}'.format(i) ,
                        'min_value' : 1,
                        'max_value' : 100,
                        'type' : variables[i][1],
                        'decimal_places' : 2
                    }
                },
            })
        )
    string_variables = parse_noun(sentences)
    template = ""
    for variable in variable_names:
        for i in range(len(words)):
            if words[i] == variable[0]:
                words[i] = '[{}]'.format(variable[1]['var'])
    template = ' '.join(words)
    for variable in string_variables:
        template = re.sub( " {} ".format(variable["default"]) , " [{}] ".format(variable["name"]), template )
    return template, variable_names, string_variables
    
if __name__ == '__main__':
    ex1 = """
		You throw a ball straight up in the air with an initial speed of 40 m/s. [g = 9.8 m/s2]. Write a
        code to determine the maximum height (H) the ball rise from the release point?
    """
    ans1 = """
            x = 40
            g = 9.8
            H = 2*x/g
            """ 
    question, variable, noun = parse_question_v2(ex1)
    #noun = parse_noun(ex1)
    print noun, 
    print question, variable
    answer = parse_answer_v2(ans1, variable)
    print answer
			
		

		

