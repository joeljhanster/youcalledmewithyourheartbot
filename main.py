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
# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
from apiclient.http import MediaFileUpload
from emoji import emojize, demojize
import random
import copy

import datetime
import pytz
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext, PicklePersistence
from telegram import InlineQueryResultArticle, InputTextMessageContent, bot, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging

# Enable logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                      level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.ERROR)

# logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

WRITE_WORD, UPLOAD_PHOTO, INSERT_TITLE, INSERT_CAPTION, SELECT_DATE = range(5)
commands = ['/start', '/write', '/journal', '/viewjournal', '/date']

# Blogger
BLOG_ID = "4868757922382507011"
SCOPES = ['https://www.googleapis.com/auth/blogger', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/documents.readonly']

# Google Docs
ENCOURAGEMENT_DOCUMENT_ID = '1X7_sLXuItIkqqVcNGxIUee1Jr6PH-tUbuJRpHNyrgeg'    # Daily Encouragement

# Telegram ID
tele_id = "41459978"

# Special Dates
day0 = datetime.date(2020,5,17)     # Anniversary
p_bday = datetime.date(1999,2,25)   # Sca's birthday
j_bday = datetime.date(1997,4,17)   # Han's birthday
v_day = datetime.date(2021,2,14)    # 1st Valentine's Day

today_testing = datetime.date(2020,5,6)  # Testing Day

title_text = []
filePath = []
chatId = []             # Get Presca's tele Id and append to this list
used = []               # Used list for encouragements

# START: SHE SAID YES!
def start(update, context):
    welcome_message = emojize("Hello Sca! Welcome to a whole new journey with Han :blush::blush::blush:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, reply_markup=ReplyKeyboardRemove())
    context.bot.send_message(chat_id=tele_id, text="{} said YES!".format(update.message.from_user.first_name))
    if update.effective_chat.id not in chatId:
        chatId.append(update.effective_chat.id)

# WRITE: SUPPORT EACH OTHER WITH A WORD OF ENCOURAGEMENT!
def write(update, context):
    message = emojize("Surprise your lover with a word of encouragement! :heart:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
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
            context.bot.send_message(chat_id=tele_id, text=update.message.text) # testing
            sent_message = emojize("Your partner should have received your word of encouragement! :+1:", use_aliases=True)
            context.bot.send_message(chat_id=id, text=sent_message)
    return ConversationHandler.END

# JOURNAL: STORE OUR FAVOURITE PHOTOS AND CAPTION IT! LET'S KEEP OUR MEMORIES!
def journal(update, context):
    # Prompt user to upload a picture
    message = emojize("Have a memory that you wish to add to the journal? First upload a photo! :camera:", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    return UPLOAD_PHOTO

def photo(update, context):
    # Retrieve photo and download it
    now = datetime.datetime.now()
    timestr = now.strftime("%d%m%Y-%H:%M:%S")
    fileName = "{}.png".format(timestr)
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(fileName)
    filePath.append(fileName)

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
    # message = message.encode('utf-8')             # Remove for Python 2

    drive_handler, blog_handler = get_blogger_service_obj()
    url = get_drive_information(drive_handler,filePath[-1])
    get_blog_information(blog_handler)

    try:
        data = {
            "content": "<p style='float: left; width: auto; margin-left: 5px; margin-bottom: 5px; text-align: justify: font-size: 14pt;'><img src = {} style = 'width:100%;height:100%'><br>{}</p>".format(url, message),
            "title": title_text[-1],
            "blog": {
                "id": BLOG_ID
            }
        }
        
        ### TODO: Delete photo generated after storing into Google Drive
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

# VIEWJOURNAL: LET'S VISIT MEMORY LANE!
def viewjournal(update, context):
    # Opens up the blogger website for browsing
    message = emojize("Here's where all the memories are stored:\nhttps://youcalledmewithyourheart.blogspot.com/", use_aliases=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())

# DATE: MAKE DATING FUN WITH WILD IDEAS!
def date(update, context):
    ### TODO: Show different options for each category of dating ideas ###
    message = emojize("Select the category!", use_aliases=True)
    adventure_keyboard = KeyboardButton(text="Adventure")
    overseas_keyboard = KeyboardButton(text="Overseas")
    custom_keyboard = [[adventure_keyboard], [overseas_keyboard]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True))
    return SELECT_DATE

def generate_date(update, context):
    boolean = check_commands(update.message.text)
    if boolean:
        return cancel(update, context)

    ### TODO: Reply with a random idea message based on the category chosen ###
    message = emojize(update.message.text, use_aliases=True)
    if message == "Adventure":
        idea = "Skuba Diving!!!"
    elif message == "Overseas":
        idea = "Phuket!"

    try:
        for id in chatId:
            date_message = emojize("{0} wants to go {1}\n\n{2}".format(update.message.from_user.first_name, message, idea))
            context.bot.send_message(chat_id=id, text=date_message, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    except Exception as ex:
        error_message = emojize("Select one of the options below!", use_aliases=True)

        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s cancelled the conversation.", user.first_name)
    return ConversationHandler.END

def daily_encouragement(context):
    today = convert_utc()
    timedelta = today - day0
    diff_days = timedelta.days
    ### TODO: AUTO-GENERATE MESSAGES TO BE SHARED DAILY, CAN BE BIBLE VERSES, QOTD, LOVE MESSAGES, WORDS OF ENCOURAGEMENT ###
    print ("Every daily interval")
    service = get_docs_service_obj()
    document = service.documents().get(documentId=ENCOURAGEMENT_DOCUMENT_ID).execute()
    message = select_encouragement(document, diff_days)

    for id in chatId:
        context.bot.send_message(chat_id=id, text=message)

def select_encouragement(document, diff_days):
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
    used.append(used_sentence)
    sentence_lst.remove(used_sentence)
    header = emojize("Together for {} days :two_hearts:\n\n".format(diff_days), use_aliases=True)
    header += used_sentence
    # header = header.encode('utf-8')   ### uncomment for Python 2
    return header    # converts unicode to string

def special_day(context):
    today = convert_utc()
    today_year, today_month, today_day = special_date(today)
    anni_year, anni_month, anni_day = special_date(day0)        # Anniversary
    pday_year, pday_month, pday_day = special_date(p_bday)      # Sca's birthday
    jday_year, jday_month, jday_day = special_date(j_bday)      # Han's birthday
    vday_year, vday_month, vday_day = special_date(v_day)       # Valentine's Day

    test_year, test_month, test_day = special_date(today_testing)

    print("Checking for special day")

    if (today_month, today_year) == (anni_month, anni_day):
        message = emojize("It is our anniversary! :smile:", use_aliases=True)

    elif (today_month, today_day) == (pday_month, pday_day):
        message = emojize("It is Sca's Birthday! :smile:", use_aliases=True)

    elif (today_month, today_day) == (jday_month, jday_day):
        message = emojize("It is Han's Birthday! :smile:", use_aliases=True)

    elif (today_month, today_day) == (vday_month, vday_day):
        message = emojize("It is Valentine's Day! :smile:", use_aliases=True)

    elif (today_month, today_day) == (test_month, test_day):
        message = emojize("I AM ONLY TESTING! :smile:", use_aliases=True)
        # message = emojize("It is our anniversary! :smile:", use_aliases=True)   # Testing anniversary message
        # message = emojize("It is Sca's Birthday! :smile:", use_aliases=True)    # Testing Sca's birthday message
        # message = emojize("It is Han's Birthday! :smile:", use_aliases=True)    # Testing Han's birthday message
        # message = emojize("It is Valentine's Day! :smile:", use_aliases=True)   # Testing Valentine's Day message

    else:
        message = ""
        print("Everyday is a special day")

    if message != "":
        for id in chatId:
            context.bot.send_message(chat_id=id, text=message)

def special_date(date):
    year = date.year
    month = date.month
    day = date.day
    
    return year, month, day

# INVALID COMMAND
def unknown(update, context):
    message = emojize(update.message.text, use_aliases=True)
    if message not in commands:
        message = emojize("You are loved! Maybe you want to type another command? :smile:", use_aliases=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Function to check if message starts with "/"
def check_commands(message):
    message = emojize(message, use_aliases=True)
    if (message[0] == '/'):
        logger.info('Message starts with "/"')
        return True
    else:
        return False

# Function to get credentials
def get_credentials():
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
    return creds

# Function to generate the blogger and drive service
def get_blogger_service_obj():
    creds = get_credentials()
    blog_service = build('blogger', 'v3', credentials = creds)
    drive_service = build('drive', 'v3', credentials = creds)
    return drive_service, blog_service

def get_docs_service_obj():
    creds = get_credentials()
    docs_service = build('docs', 'v1', credentials = creds)
    return docs_service

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

# Function to convert utc time to local Singapore time (datetime.datetime -> datetime.date)
def convert_utc():
    local_tz = pytz.timezone('Asia/Singapore')
    my_time = datetime.datetime.utcnow()
    my_time = my_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return datetime.date(my_time.year, my_time.month, my_time.day)

# Function to convert utc time to local Singapore time (datetime.time)
def convert_time(time):
    new_hour = time.hour-8  # Asia/Singapore (GMT +8)
    if (new_hour < 0):
        new_hour = 24 + new_hour
    return time.replace(hour=new_hour)

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
                    CommandHandler('viewjournal', cancel),
                    CommandHandler('date', cancel)]
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

    date_handler = ConversationHandler(
        entry_points = [CommandHandler('date', date)],
        states = {
            SELECT_DATE: [MessageHandler(Filters.text, generate_date)]
        },
        fallbacks = [CommandHandler('start', cancel),
                    CommandHandler('write', cancel),
                    CommandHandler('journal', cancel),
                    CommandHandler('viewjournal', cancel),
                    CommandHandler('date', cancel)]
    )
    dispatcher.add_handler(date_handler,2)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler,3)

    # JOB QUEUE
    ### TODO: CHECK WHETHER THE REMINDER IS SET CORRECTLY ###
    job = updater.job_queue

    # TESTING
    job.run_repeating(daily_encouragement, interval=5, first=0) # Daily Encouragments
    # job.run_repeating(special_day, interval=10, first=0) # Check if it is a special day


    # ACTUAL
    job.run_repeating(daily_encouragement, interval=86400, first=convert_time(datetime.time(17,5,17,5))) # Daily Encouragments
    job.run_repeating(special_day, interval=86400, first=convert_time(datetime.time(0,0,0,0))) # Check if it is a special day

    ### TODO: MAKE THE TELEGRAM BOT PERSISTENT ###
    print("Starting telegram bot")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()