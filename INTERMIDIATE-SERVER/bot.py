import os
import requests
import base64
import json
from io import BytesIO
from PIL import Image


TOKEN =  os.environ.get('TELEGRAM_TOKEN', None)
web_url = os.environ.get('WEB_URL', None)
URL = os.environ.get('Lambda_URL', None)



import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    user = update.message.from_user
    """Send a message when the command /help is issued."""
    update.message.reply_text("""Bonjour %s je suis Emma, si vous envoyez /question je vais vous poser une question qui existe dans mon esprit en sautant que vous y répondiez """%user['username'])


def info(update,context):
    user = update.message.from_user
    update.message.reply_text('You are the user {} and your user ID: {} '.format(user['username'], user['id']))


def photo(update, context):
    print("receive image")
    file = context.bot.get_file(update.message.photo[-1].file_id)
    
    f =  file.download_as_bytearray()
    print(type(f))

    payload = f
    im_b64 = base64.b64encode(payload).decode("utf8")
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    payload = json.dumps({"image": im_b64, "other_key": "value"})

    res = requests.post(url=URL, data=payload, headers=headers)

    # print(res)
    result = res.text

    if "message" in result:
        imageStream = BytesIO(file.download_as_bytearray())
        imageFile = Image.open(imageStream)
        imageFile.save("test.jpg")
        with open('test.jpg', 'rb') as img:
            payload = img.read()
        res = requests.post(url=URL, data=payload, headers=headers)
        result = res.text
        
    print("++++",result)

    out = list(map(float,result.split()))
    print("out ",out)

    thresholds  = {  'complex': 0.43765415,
                     'frog_eye_leaf_spot': 0.42971102,
                     'healthy': 0.40393935,
                     'powdery_mildew': 0.79799781,
                     'rust': 0.52101797,
                     'scab': 0.52179047}

    labels = [ "complex" ,"frog_eye_leaf_spot","healthy","powdery_mildew","rust","scab"]

    response = """I procsseed that and the result was : """

    print("start loop")
    P = []
    for i in range(len(labels)):
        P.append([int(out[i]*100),labels[i]])
    P.sort()
    for p in P[::-1]:
        response+=f"\n{p[1]}>> {p[0]}%"
    print("end loop")


    print(response)
    context.bot.send_message(chat_id=update.message.chat_id, text=response)




def reply(update, context):
    text = update.message.text
    # if(text=="Bonjour tout le monde"):return help(update, context)
    #update.message.reply_text(update.message.text)
    #update.message.reply_photo(photo='https://telegram.org/img/t_logo.png') # replay to bot
    # update.message.reply_photo(open("downloand.png","rb"))
    # user = update.message.from_user
    # print(user)
    # update.message.reply_text(text)
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))

    # on noncommand i.e message - reply the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, reply))
    
    dp.add_handler(MessageHandler(Filters.photo, photo))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(web_url + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()