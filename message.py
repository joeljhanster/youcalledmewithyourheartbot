# Python file to generate all the messages required for the Telegram Bot
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from emoji import emojize
import random
import copy

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
ENCOURAGEMENT_ID = '1X7_sLXuItIkqqVcNGxIUee1Jr6PH-tUbuJRpHNyrgeg'   # Daily Encouragement
SCA_BDAY_ID = '1l2Z5OaAGvThcKl8gV_UG7TibeRZcifKCZrk_1YEJRRs'        # Sca's Birthday Wishes
HAN_BDAY_ID = '1GFWs2CLi6pgAkGNZdL3f72s6z4F7gTUjWf0umh5pJaQ'        # Han's Birthday Wishes
ANNIVERSARY_ID = '1BafCtdVX3K83XorhrtP_RHip3Tm6abyO6K14VomdCNo'     # Anniversary Wishes
VDAY_ID = '1rlurNZuwP64XeDrQ1fB2Tf_-Y5TQ_4RSwcrhizTOeik'            # Valentine's Day Wishes
XMAS_ID = '1oMUFCsPRxXmpc9NSx1Zy_8-FtwjiXeio0DlEbpu8STY'            # Christmas Wishes
ADVENTURE_ID = '1NjLSUb4_AO3AVJMvzhIEIn-Gj6EPtvzH_Wz-U_gsGec'       # Adventure Dates
OVERSEAS_ID = '1A9YNtzjhJbNw-8748HCXMA4haMRdgzL-ff7e_jB6rAQ'        # Overseas Dates
CHILL_ID = '1wMemluKDnRZKGf25cNYvr5Y-IO_oo4BQ2eDOFan13pM'           # Chill Dates
MOVIE_ID = '1hz_xBIl8dDEUnezoQp1lYje9hSFNbb51jjKWCOnUYaY'           # Movie Dates
ID_LIST = [ENCOURAGEMENT_ID, SCA_BDAY_ID, HAN_BDAY_ID, ANNIVERSARY_ID, VDAY_ID, XMAS_ID, ADVENTURE_ID, OVERSEAS_ID, CHILL_ID, MOVIE_ID]

used = []

def main():
    creds = None
    if os.path.exists('auth_token.pickle'):
        with open('auth_token.pickle', 'rb') as token:
            # creds = pickle.load(token, encoding='latin1')   # for heroku app
            creds = pickle.load(token)    # for local
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret_1044751721266-cbvnnlkrfuuogp35but2hon3ia31ld33.apps.googleusercontent.com.json', SCOPES)
            flow.run_console()
            creds = flow.credentials
        # Save the credentials for the next run
        with open('auth_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)

    # title_lst = ["Sca's Birthday Wishes", "Han's Birthday Wishes", "Anniversary Wishes", "Valentine's Day Wishes", "Christmas Wishes", "Adventure Dates", "Overseas Dates", "Chill Dates", "Movie Dates"]
    # for element in title_lst:
    #     title = element
    #     body = {
    #         'title': title
    #     }
    #     doc = service.documents() \
    #         .create(body=body).execute()
    #     print('Created document with title: {0}'.format(
    #         doc.get('title')))


    # Retrieve the documents contents from the Docs service.
    # document = service.documents().get(documentId=PBDAY_ID).execute()
    for documentID in ID_LIST:
        document = service.documents().get(documentId=documentID).execute()
        print('Browsing through document with title: {0}'.format(document.get('title')))
        select_encouragement(document)

def select_encouragement(document):
    content = document.get('body').get('content')
    num_lines = len(content)
    count = 0   # count number of line breaks
    sentence = ""
    sentence_lst = []

    # Store unused encouragements into sentence_lst
    for i in range(1,num_lines):
        message = content[i].get('paragraph').get('elements')[0].get('textRun').get('content')
        if message == '\n':
            if (sentence not in used and sentence != ""):
                sentence_lst.append(sentence)
            sentence = ""
        else:
            sentence += message
            if i == num_lines-1:    # check if last line
                sentence_lst.append(sentence)
                sentence = ""
    
    # If all the encouragements are used, reset
    if (len(sentence_lst) == 0):
        sentence_lst = copy.copy(used)
        del used[:]

    used_sentence = random.choice(sentence_lst)
    print (used_sentence)
    used.append(used_sentence)
    sentence_lst.remove(used_sentence)
    # print ("Used lst: " + str(used))
    # print ("Sentence lst: " + str(sentence_lst))

if __name__ == '__main__':
    main()