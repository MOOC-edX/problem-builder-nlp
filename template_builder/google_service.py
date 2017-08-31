
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials

from pprint import pprint
import re

# from googleapiclient import discovery

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None




# # If modifying these scopes, delete your previously saved credentials
# # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
# CLIENT_SECRET_FILE = 'google_sheets_client_secret.json'
# APPLICATION_NAME = 'Google Sheets API'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('./')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')
    # credential_path = os.path.join(credential_dir,
    #                                'google_sheets_client_secret.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_credentials_by_service_account():
    # use service account of Tam:
    # CLIENT_SECRET_FILE = '/edx/app/edxapp/google-service/service-account/service_account.json'
    # APPLICATION_NAME = 'Drive API Python Quickstart'
    # SCOPES = ['https://www.googleapis.com/auth/drive']

    # use service account: canhdq-mooc-edx
    CLIENT_SECRET_FILE = '/edx/app/edxapp/google-service/service-account/dqcanh-mooc-edx-gsaccount.json'
    APPLICATION_NAME = 'Google Drive API Python'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    print('Client secret file: ' + CLIENT_SECRET_FILE)

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CLIENT_SECRET_FILE, scopes=SCOPES)
    print("credentials:")
    pprint(credentials)

    return credentials


class gsheets():
    def check_answer(self, teacher_answer, student_answer):

        print('Raw teacher answer:' + teacher_answer)
        print('Raw student answer:' + student_answer)

        # format answer input strings:
        teacher_answer = teacher_answer.replace(' ','')     # get rig of space character
        teacher_answer_list = teacher_answer.split('=')
        teacher_answer = '=' + teacher_answer_list[-1]

        student_answer = student_answer.replace(' ', '')    # get rig of space character
        student_answer_list = student_answer.split('=')
        student_answer = '=' + student_answer_list[-1]

        print('Expected teacher answer:' + teacher_answer)
        print('Expected student answer:' + student_answer)

        # create a new spreadsheet to store data
        # spreadsheet_body = {
        #     # TODO: Add desired entries to the request body.
        # }

        # credentials = get_credentials()   # use client ID
        credentials = get_credentials_by_service_account()  # use service account

        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)
        spreadsheet_body = {
            "properties": {
                "title": "Problem Grading Template",
                "locale": "en_US",
                "autoRecalc": "ON_CHANGE",
                "timeZone": "Asia/Jakarta"
            }
        }

        request = service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        print('Answer template file:')
        pprint(response)

        sheets = response['sheets']
        for s in sheets:
            properties = s['properties']
            break

        # Update answer data to the newly created spreadsheets, Sheet1
        title = properties['title']
        spreadsheet_id = response["spreadsheetId"]
        rangeName = title + "!A2:B2"
        body = {
            "range": rangeName,
            "majorDimension": 'ROWS',
            "values": [
                [teacher_answer, student_answer]
            ],
        }
        # call REST API to update spreadsheets
        request = service.spreadsheets().values().update(
            spreadsheetId = spreadsheet_id,
            range=rangeName,
            valueInputOption = 'USER_ENTERED',
            body = body
        )
        response = request.execute()
        # print('Updated answer inputs:')
        # pprint(response)

        # Get answer's value to compare

        # The A1 notation of the values to retrieve.
        range_ = rangeName  # TODO: Update placeholder value.

        # How values should be represented in the output.
        # The default render option is ValueRenderOption.FORMATTED_VALUE.
        value_render_option = 'UNFORMATTED_VALUE'  # TODO: Update placeholder value.

        # How dates, times, and durations should be represented in the output.
        # This is ignored if value_render_option is
        # FORMATTED_VALUE.
        # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
        date_time_render_option = 'FORMATTED_STRING'  # TODO: Update placeholder value.

        request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_,
                                                      valueRenderOption=value_render_option,
                                                      dateTimeRenderOption=date_time_render_option)
        response = request.execute()

        # TODO: Change code below to process the `response` dict:
        print('Get answer output values to compare:')
        pprint(response)

        # extract values to compare
        teacher_answer_value = response['values'][0][0]
        student_answer_value = response['values'][0][1]
        pprint(teacher_answer_value)
        pprint(student_answer_value)

        if student_answer_value == teacher_answer_value:
            print('Correct')
            return True
        else:
            print('Inccorrect')

        return False


    def check_answer_sheet(self, student_answer_spreadsheetId, teacher_answer_spreadsheetId, data_range):
        '''
        Validate answer base on answer spreadsheets of student and teacher from google spreadsheets (URL)

        :param student_answer_spreadsheetId: https://docs.google.com/spreadsheets/d/15Hlu3jCJjEzKgvMdMle5c2KwEri2HGDSQKiLbh_V8JU/edit
        :param teacher_answer_spreadsheetId: https://docs.google.com/spreadsheets/d/1uQfNkOefkDBHFIPsa_I-Bo8VgLzUPOu4faaEhLk0hT8/edit
        :return: boolean True/False

        :author: canhdq
        '''

        result = False

        print('Teacher answer spreadsheetId:' + teacher_answer_spreadsheetId)
        print('Student answer spreadsheetId:' + student_answer_spreadsheetId)

        # # format answer input strings:
        # formatted_url_teacher_answer = url_teacher_answer.replace(' ', '')  # get rig of space if any
        #
        # spreadsheetId_teacher_answer = formatted_url_teacher_answer.split('/d/') #
        # spreadsheetId_teacher_answer = spreadsheetId_teacher_answer[-1]
        # spreadsheetId_teacher_answer = re.sub()
        #
        # student_answer = student_answer.replace(' ', '')  # get rig of space character
        # student_answer_list = student_answer.split('=')
        # student_answer = '=' + student_answer_list[-1]
        #
        # print('Expected teacher answer:' + teacher_answer)
        # print('Expected student answer:' + student_answer)


        # credentials = get_credentials()   # use client ID
        credentials = get_credentials_by_service_account()  # use service account

        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        # Read answer data from spreadsheet
        #

        # The A1 notation of answer data
        range_student_answer = data_range
        range_teacher_answer = data_range

        # How values should be represented in the output.
        # The default render option is ValueRenderOption.FORMATTED_VALUE.
        value_render_option = 'UNFORMATTED_VALUE'  # TODO: Update placeholder value.

        # How dates, times, and durations should be represented in the output.
        # This is ignored if value_render_option is
        # FORMATTED_VALUE.
        # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
        date_time_render_option = 'FORMATTED_STRING'  # TODO: Update placeholder value.

        # get student answer file
        #
        spreadsheetId = student_answer_spreadsheetId
        range_ = range_student_answer  # TODO: Update placeholder value.

        request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_,
                                                      valueRenderOption=value_render_option,
                                                      dateTimeRenderOption=date_time_render_option)
        response = request.execute()
        # extract value
        student_answer_value = response['values'][0][0]
        print('Student answer data:')
        pprint(response)

        # get teacher answer file
        #
        spreadsheetId = teacher_answer_spreadsheetId
        range_ = range_teacher_answer  # TODO: Update placeholder value.

        request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_,
                                                      valueRenderOption=value_render_option,
                                                      dateTimeRenderOption=date_time_render_option)
        response = request.execute()
        # extract value
        teacher_answer_value = response['values'][0][0]
        print('Teacher answer data:')
        pprint(response)

        print('Teacher answer value:')
        pprint(teacher_answer_value)
        print('Student answer value:')
        pprint(student_answer_value)

        if student_answer_value == teacher_answer_value:
            print('Correct')
            result = True
        else:
            print('Inccorrect')
            result = False

        return result



def main():

    # """Shows basic usage of the Sheets API.
    #
    # Creates a Sheets API service object and prints the names and majors of
    # students in a sample spreadsheet:
    # https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    # """
    # credentials = get_credentials()
    #
    # print('Credentials:')
    # pprint(credentials)
    #
    # http = credentials.authorize(httplib2.Http())
    # discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
    #                 'version=v4')
    # service = discovery.build('sheets', 'v4', http=http,
    #                           discoveryServiceUrl=discoveryUrl)

    # spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    # rangeName = 'Class Data!A2:E'
    # # spreadsheetId = '1uQfNkOefkDBHFIPsa_I-Bo8VgLzUPOu4faaEhLk0hT8'
    # # rangeName = 'Answer!A2:E'
    # result = service.spreadsheets().values().get(
    #     spreadsheetId=spreadsheetId, range=rangeName).execute()
    # values = result.get('values', [])
    #
    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         print('%s, %s' % (row[0], row[4]))
    #
    # print('Creating new spreadsheet.')
    # spreadsheet_body = {
    #     # TODO: Add desired entries to the request body.
    # }
    #
    # request = service.spreadsheets().create(body=spreadsheet_body)
    # response = request.execute()
    # # TODO: Change code below to process the `response` dict:
    # pprint(response)

    print('Calling Google Spreadsheets to check answer...')
    sheets = gsheets()

    # teacher_answer = 'x=SUM(5,9)'
    # student_answer = 'x = 5 -9'
    # sheets.check_answer(teacher_answer,student_answer)

    # student_spreadsheetId = '1sxt5Eo9NqOlHa3lbK7-hAgVm3To5D5W_s4X6WNFChBE'
    # teacher_spreadsheetId = '1sxt5Eo9NqOlHa3lbK7-hAgVm3To5D5W_s4X6WNFChBE'

    student_spreadsheetId = '1uQfNkOefkDBHFIPsa_I-Bo8VgLzUPOu4faaEhLk0hT8'
    teacher_spreadsheetId = '1uQfNkOefkDBHFIPsa_I-Bo8VgLzUPOu4faaEhLk0hT8'

    data_range = "A2"
    sheets.check_answer_sheet(teacher_spreadsheetId, student_spreadsheetId, data_range)




if __name__ == '__main__':
    main()
