# This bot is made with love <3
import datetime
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, bot
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

WRITE_WORD, UPLOAD_PHOTO, INSERT_CAPTION = range(3)

day0 = datetime.date(2020,5,17)
chatId = []

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello Presca! Welcome to a whole new journey with Joel :)")
    if update.effective_chat.id not in chatId:
        chatId.append(update.effective_chat.id)

# WRITE: SUPPORT EACH OTHER WITH A WORD OF ENCOURAGEMENT!
def write(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Surprise your lover with a word of encouragement! <3")
    return WRITE_WORD

def word(update, context):
    for id in chatId:
        if id != update.effective_chat.id:
            context.bot.send_message(chat_id=id, text="Your partner has a word of encouragement for you! Remember to show your appreciation!")
            context.bot.send_message(chat_id=id, text=update.message.text)
        else:
            context.bot.send_message(chat_id=id, text="Your partner should have received your word of encouragement!")
    return ConversationHandler.END

# JOURNAL: STORE OUR FAVOURITE PHOTOS AND CAPTION IT! LET'S KEEP OUR MEMORIES!
def journal(update, context):
    # Prompt user to upload a picture
    context.bot.send_message(chat_id=update.effective_chat.id, text="Have a memory that you wish to add to the journal? First upload a photo!")
    return UPLOAD_PHOTO

def photo(update, context):
    # Retrieve photo and download it
    now = datetime.datetime.now()
    timestr = now.strftime("%d%m%Y-%H:%M:%S")
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("{}.jpg".format(timestr))

    # Prompt user to write a description of the photo
    update.message.reply_text("Now write a story about this photo! <3")
    return INSERT_CAPTION

def caption(update, context):
    # Record the description of the photo and store it into the blog
    message = update.message.text
    print (message)
    update.message.reply_text("The blog has been updated! Type /viewjournal to take a look!")
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# VIEWJOURNAL: LET'S VISIT MEMORY LANE!
def viewjournal(update, context):
    # Opens up the blogger website for browsing
    context.bot.send_message(chat_id=update.effective_chat.id, text="Here's where all the memories are stored:\nhttps://youcalledmewithyourheart.blogspot.com/")

def daily_encouragement(context):
    timedelta = datetime.date.today() - day0
    diff_days = timedelta.days
    ### TODO: AUTO-GENERATE MESSAGES TO BE SHARED DAILY, CAN BE BIBLE VERSES, QOTD, LOVE MESSAGES, WORDS OF ENCOURAGEMENT ###
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Day {}: I love you".format(diff_days))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You are loved! Maybe you want to type another command? :)")

### TODO: REMOVE THIS FUNCTION ###
def callback_minute(context):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Time now is: {}".format(current_time))

def main():
    updater = Updater(token='1032322197:AAHQm4mkuvVu7RLA56vLuX_RZ-_Ph9tfZp8', use_context=True)   # INSERT TOKEN
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    ### TODO: MAKE SURE THAT THE CONVERSATIONS END BEFORE MAKING THE NEXT COMMAND ###
    write_handler = ConversationHandler(
        entry_points = [CommandHandler('write', write)],
        states = {
            WRITE_WORD: [MessageHandler(Filters.text, word)]
        },
        fallbacks = [CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(write_handler)

    journal_handler = ConversationHandler(
        entry_points = [CommandHandler('journal', journal)],
        states = {
            UPLOAD_PHOTO: [MessageHandler(Filters.photo, photo)],
            INSERT_CAPTION: [MessageHandler(Filters.text, caption)]
        },
        fallbacks = [CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(journal_handler)

    viewjournal_handler = CommandHandler('viewjournal', viewjournal)
    dispatcher.add_handler(viewjournal_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # JOB QUEUE
    ### TODO: CHECK WHETHER THE REMINDER IS SET CORRECTLY ###
    job = updater.job_queue
    job.run_daily(daily_encouragement, time = datetime.time(20,8,5,5))
    # print(job.jobs())
    # j = updater.job_queue
    # j.run_repeating(callback_minute, interval=5, first=0)
    # print(j.jobs())

    ### TODO: MAKE THE TELEGRAM BOT PERSISTENT ###
    print("Starting telegram bot")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()