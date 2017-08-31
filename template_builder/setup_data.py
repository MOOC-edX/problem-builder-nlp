import mysql.connector
from mysql.connector import errorcode
import settings as s


def create_dummy_data(xblock_id):
    """
        INSERT INTO edxapp.gqb_question_template (xblock_id, question_template) VALUES (?, ?)

        INSERT INTO edxapp.gqb_variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (?, a, int, 0, 10)
        INSERT INTO edxapp.gqb_variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (?, b, int, 10, 100)
    """
    
    connection = mysql.connector.connect(**s.database)
    cursor = connection.cursor()
    
    # create question template
    question_template_query = "INSERT INTO edxapp.gqb_question_template (xblock_id, template) VALUES ('" + xblock_id + "', " + "'Given a and b'" + ")"
    question_template_cursor = connection.cursor()
    question_template_cursor.execute(question_template_query)
    question_template_cursor.close()

    
    # create variables
    variable_template_query = "INSERT INTO edxapp.gqb_variable (xblock_id, name, type, min_value, max_value, decimal_places) VALUES (%s, %s, %s, %s, %s, %s)"
    
    # "a" variable
    a_variable_data = (xblock_id, 'a', 'int', 0, 10, 2)
    cursor.execute(variable_template_query, a_variable_data)
    
    # "b" variable
    b_variable_data = (xblock_id, 'b', 'int', 0, 10, 3)
    cursor.execute(variable_template_query, b_variable_data)
    
    
    connection.commit()
    cursor.close()


if __name__ == "__main__":
    xblock_id_1 = "block-v1:Home+CS107+2017_T1+type@formula_exercise_block+block@3d06adc38f334114a475eab3518862dd"
    create_dummy_data(xblock_id_1)
    
    xblock_id_2 = "block-v1:Home+CS107+2017_T1+type@formula_exercise_block+block@ebff890deebe4a39a3844ecf17e6e187"
    create_dummy_data(xblock_id_2)
