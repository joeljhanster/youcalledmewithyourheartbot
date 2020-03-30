# This bot is made with love <3
import datetime
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, bot
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

UPLOAD_PHOTO, INSERT_CAPTION = range(2)

day0 = datetime.date(2020,5,17)
chatId = []

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello Presca! Welcome to a whole new journey with Joel :)")
    if update.effective_chat.id not in chatId:
        chatId.append(update.effective_chat.id)

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
    
    # 
    print (message)
    update.message.reply_text("The blog has been updated! Type /viewjournal to take a look!")
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def daily_encouragement(context):
    timedelta = datetime.date.today() - day0
    diff_days = timedelta.days
    # Edit message here using random generator
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Day {}: I love you".format(diff_days))

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You are loved! Maybe you want to type another command? :)")

def callback_minute(context):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    for id in chatId:
        context.bot.send_message(chat_id=id, text="Time now is: {}".format(current_time))

def main():
    updater = Updater(token='1032322197:AAHQm4mkuvVu7RLA56vLuX_RZ-_Ph9tfZp8', use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    journal_handler = ConversationHandler(
        entry_points = [CommandHandler('journal', journal)],
        states = {
            UPLOAD_PHOTO: [MessageHandler(Filters.photo, photo)],
            INSERT_CAPTION: [MessageHandler(Filters.text, caption)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(journal_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # JOB QUEUE
    job = updater.job_queue
    job.run_daily(daily_encouragement, time = datetime.time(20,8,5,5))
    # print(job.jobs())
    # j = updater.job_queue
    # j.run_repeating(callback_minute, interval=5, first=0)
    # print(j.jobs())

    print("Starting telegram bot")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()