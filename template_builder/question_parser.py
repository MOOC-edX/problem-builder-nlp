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



def parse_question(sentences):

    words = tokenization(ex1)
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
    template = ""
    for variable in variable_names:
        for i in range(len(words)):
            if words[i] == variable[0]:
                words[i] = '[{}]'.format(variable[1]['var'])
                
                print words[i]

    template = ' '.join(words)
    return template, variable_names
    
if __name__ == '__main__':
	ex1 = """
		You throw a ball straight up in the air with an initial speed of 40 m/s. [g = 9.8 m/s2]. Write a
        code to determine the maximum height (H) the ball rise from the release point?
	"""
	question, variable = parse_question(ex1)
	print question, variable
			
		

		

