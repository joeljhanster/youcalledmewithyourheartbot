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
DOCUMENT_ID = '1X7_sLXuItIkqqVcNGxIUee1Jr6PH-tUbuJRpHNyrgeg'    # Daily Encouragement

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

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    for i in range(10):
        select_encouragement(document)
    

def select_encouragement(document):
    content = document.get('body').get('content')
    num_lines = len(content)
    count = 0   # count number of line breaks
    sentence = ""
    sentence_lst = []

    # Store unused encouragements into sentence_lst
    for i in range(1,num_lines):
        message = emojize(content[i].get('paragraph').get('elements')[0].get('textRun').get('content'), use_aliases=True)
        if message == '\n':
            if (sentence not in used):
                sentence_lst.append(sentence)
            sentence = ""
        else:
            sentence += message
    
    # If all the encouragements are used, reset
    if (len(sentence_lst) == 0):
        sentence_lst = copy.copy(used)
        del used[:]

    used_sentence = random.choice(sentence_lst)
    print (used_sentence)
    used.append(used_sentence)
    sentence_lst.remove(used_sentence)
    print ("Used lst: " + str(used))
    print ("Sentence lst: " + str(sentence_lst))

if __name__ == '__main__':
    main()