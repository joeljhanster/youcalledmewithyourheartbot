# This bot is made with love <3
import sys
import os
import pickle
import json
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from apiclient.http import MediaFileUpload
from emoji import emojize

import datetime
import pytz
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext, PicklePersistence
from telegram import InlineQueryResultArticle, InputTextMessageContent, bot
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

WRITE_WORD, UPLOAD_PHOTO, INSERT_TITLE, INSERT_CAPTION = range(4)
commands = ['/start', '/write', '/journal', '/viewjournal']

# Blogger
BLOG_ID = "4868757922382507011"
SCOPES = ['https://www.googleapis.com/auth/blogger', 'https://www.googleapis.com/auth/drive.file']

# Telegram ID
tele_id = "41459978"

# Special Dates
day0 = datetime.date(2020,5,17)
p_bday = datetime.date(1999,2,25)
j_bday = datetime.date(1997,4,17)

title_text = []
filePath = []
chatId = []

def start(update, context):
    welcome_message = emojize("Hello Presca! Welcome to a whole new journey with Joel :blush::blush::blush:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)
    context.bot.send_message(chat_id=tele_id, text="{} said YES!".format(update.message.from_user.first_name))
    if update.effective_chat.id not in chatId:
        chatId.append(update.effective_chat.id)

# WRITE: SUPPORT EACH OTHER WITH A WORD OF ENCOURAGEMENT!
def write(update, context):
    message = emojize("Surprise your lover with a word of encouragement! :heart:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return WRITE_WORD

def word(update, context):
    boolean = check_commands(update.message.text)
    if boolean:
        return cancel(update, context)

    for id in chatId:
        if id != update.effective_chat.id:
            received_message = emojize("Your partner has a word of encouragement for you! Remember to show your appreciation! :kissing_heart:", use_aliases=True)
            context.bot.send_message(chat_id=id, text=received_message)
            context.bot.send_message(chat_id=id, text=update.message.text)
        else:
            context.bot.send_message(chat_id=id, text=update.message.text) # testing
            sent_message = emojize("Your partner should have received your word of encouragement! :+1:", use_aliases=True)
            context.bot.send_message(chat_id=id, text=sent_message)
    return ConversationHandler.END

# JOURNAL: STORE OUR FAVOURITE PHOTOS AND CAPTION IT! LET'S KEEP OUR MEMORIES!
def journal(update, context):
    # Prompt user to upload a picture
    message = emojize("Have a memory that you wish to add to the journal? First upload a photo! :camera:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return UPLOAD_PHOTO

def photo(update, context):
    # Retrieve photo and download it
    now = datetime.datetime.now()
    timestr = now.strftime("%d%m%Y-%H:%M:%S")
    fileName = "{}.png".format(timestr)
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(fileName)
    filePath.append(fileName)
    # filePath.append(os.path.abspath(fileName))

    # Prompt user to insert a title for the photo
    message = emojize("Insert a Title!!! :sparkles:", use_aliases=True)
    update.message.reply_text(message)
    return INSERT_TITLE

def title(update, context):
    boolean = check_commands(update.message.text)
    if boolean:
        return cancel(update, context)
    
    title_text.append(emojize(update.message.text, use_aliases=True))

    # Prompt user to write a description of the photo
    message = emojize("Now write a story about this photo! :black_nib:", use_aliases=True)
    update.message.reply_text(message)
    return INSERT_CAPTION

def caption(update, context):
    boolean = check_commands(update.message.text)
    if boolean:
        return cancel(update, context)

    # Record the description of the photo and store it into the blog
    message = emojize(update.message.text, use_aliases=True)
    print (message)

    drive_handler, blog_handler = get_blogger_service_obj()
    url = get_drive_information(drive_handler,filePath[-1])
    get_blog_information(blog_handler)

    try:
        ### TODO: Allow blog post to post emojis
        data = {
            "content": "<p style='float: left; width: auto; margin-left: 5px; margin-bottom: 5px; text-align: justify: font-size: 14pt;'><img src = {} style = 'width:100%;height:100%'><br>{}</p>".format(url, message),
            "title": title_text[-1],
            "blog": {
                "id": BLOG_ID
            }
        }
        
        ### TODO: Delete photo generated
        del filePath[:]
        del title_text[:]

        posts = blog_handler.posts()
        posts.insert(blogId=BLOG_ID, body=data, isDraft=False, fetchImages=True).execute()
        update_message = emojize("The blog has been updated! :heart_eyes::heart_eyes::heart_eyes:\nType /viewjournal to take a look! :fire:", use_aliases=True)
        update.message.reply_text(update_message)
    except Exception as ex:
        print(str(ex))
        failed_message = emojize("Failed to upload post! :disappointed_relieved:\nSome things just don't go according to plan but keep trying! :clap:", use_aliases=True)
        update.message.reply_text(failed_message)

    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s cancelled the conversation.", user.first_name)
    return ConversationHandler.END

# VIEWJOURNAL: LET'S VISIT MEMORY LANE!
def viewjournal(update, context):
    # Opens up the blogger website for browsing
    message = emojize("Here's where all the memories are stored:\nhttps://youcalledmewithyourheart.blogspot.com/", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def daily_encouragement(context):
    timedelta = datetime.date.today() - day0
    diff_days = timedelta.days
    ### TODO: AUTO-GENERATE MESSAGES TO BE SHARED DAILY, CAN BE BIBLE VERSES, QOTD, LOVE MESSAGES, WORDS OF ENCOURAGEMENT ###
    print ("Every daily interval")
    
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Day {}: I love you!".format(diff_days))

def unknown(update, context):
    message = emojize(update.message.text, use_aliases=True)
    if message not in commands:
        message = emojize("You are loved! Maybe you want to type another command? :smile:", use_aliases=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

### TODO: REMOVE THIS FUNCTION ###
def timecheck(context):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print ("Every callback interval")
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Time now is: {}".format(current_time))

# Function to check if message starts with "/"
def check_commands(message):
    # message = str(message)
    message = emojize(message, use_aliases=True)
    if (message[0] == '/'):
        logger.info('Message starts with "/"')
        return True
    else:
        return False

# Function to generate the blogger and drive service
def get_blogger_service_obj():
    creds = None
    if os.path.exists('auth_token.pickle'):
        with open('auth_token.pickle', 'rb') as token:
            creds = pickle.load(token, encoding='latin1')   # for heroku app
            # creds = pickle.load(token)    # for local
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
    blog_service = build('blogger', 'v3', credentials = creds)
    drive_service = build('drive', 'v3', credentials = creds)
    return drive_service, blog_service

# Function to get the blog information
def get_blog_information(api_handler=None, blog_max_posts=3):
    try:
        if not api_handler:
            return None
        blogs = api_handler.blogs()
        resp = blogs.get(blogId=BLOG_ID, maxPosts=blog_max_posts, view="ADMIN").execute()
        for blog in resp['posts']['items']:
            print ('The blog title: \'%s\' and url: %s' % (blog['title'],blog['url']))
    except Exception as ex:
        print(str(ex))

# Function to upload photo onto Google drive
def get_drive_information(api_handler,fileName):
    try:
        if not api_handler:
            return None
        file_metadata = {
        'name': fileName,
        'parents': ['1t2wesFIyraxtsA-X7-lWxrnEYnXCnnD6'],
        'mimeType': 'image/png'
        }
        media = MediaFileUpload(fileName,
                                mimetype='image/png',
                                resumable=True)
        file = api_handler.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print ('File ID: ' + file.get('id'))
        url = "http://drive.google.com/uc?export=view&id={}".format(file.get('id'))
        print ('url: ' + url)
        return url
    except Exception as ex:
        print(str(ex))


def main():
    updater = Updater(token='1032322197:AAHQm4mkuvVu7RLA56vLuX_RZ-_Ph9tfZp8', use_context=True)   # INSERT TOKEN
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler,2)

    write_handler = ConversationHandler(
        entry_points = [CommandHandler('write', write)],
        states = {
            WRITE_WORD: [MessageHandler(Filters.text, word)]
        },
        fallbacks = [CommandHandler('start', cancel),
                    CommandHandler('write', cancel),
                    CommandHandler('journal', cancel),
                    CommandHandler('viewjournal', cancel)]
    )
    dispatcher.add_handler(write_handler,1)

    journal_handler = ConversationHandler(
        entry_points = [CommandHandler('journal', journal)],
        states = {
            UPLOAD_PHOTO: [MessageHandler(Filters.photo, photo)],
            INSERT_TITLE: [MessageHandler(Filters.text, title)],
            INSERT_CAPTION: [MessageHandler(Filters.text, caption)]
        },
        fallbacks = [MessageHandler(Filters.command, cancel)]
    )
    dispatcher.add_handler(journal_handler,0)

    viewjournal_handler = CommandHandler('viewjournal', viewjournal)
    dispatcher.add_handler(viewjournal_handler,2)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler,3)

    # JOB QUEUE
    ### TODO: CHECK WHETHER THE REMINDER IS SET CORRECTLY ###
    job = updater.job_queue
    # time_scheduled = datetime.time(6,22,5,5)
    local_tz = pytz.timezone('Asia/Singapore')
    job.run_repeating(timecheck, interval=10, first=0)
    # job.run_repeating(daily_encouragement, interval=5, first=datetime.time(6,32,5,5,tzinfo=local_tz)) # GST+8: 17:5

    ### TODO: MAKE THE TELEGRAM BOT PERSISTENT ###
    print("Starting telegram bot")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()