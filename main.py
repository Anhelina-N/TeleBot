import telebot 
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import datetime

df = pd.read_excel("words.xlsx")


bot = telebot.TeleBot('5856919640:AAHgE_Y8d-JucsulngZhCMiBoUl7qqrAUMo')
user_id = ''
message_id = ''
time_zone = ''
daily_word = ''


@bot.message_handler(commands=['start', 'help'])
def welcome_and_user_id(message):
     user_id = message.chat.id
     bot.reply_to(message, "Hello, this is an English Word Bot. I am going to send you daily vocab at 9 a.m. [PT or CET time] to help you to improve your English:) ")
     start_poll(message)
    
def start_poll(message):
    markup = telebot.types.InlineKeyboardMarkup()
    option1 = telebot.types.InlineKeyboardButton("PT", callback_data="PT")
    option2 = telebot.types.InlineKeyboardButton("CET", callback_data="CET")
    markup.add(option1, option2)
    message_id = message.message_id
    bot.send_poll( 
        message.chat.id,
        "Please choose the time zone that works best for you!",
        options=["PT", "CET"],
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    poll_answer = call.data
    try:
        message = call.message
        match (poll_answer):
            case 'PT':
                time_zone = 'US/Pacific'
            case 'CET': 
                time_zone = 'Europe/Rome'
        id = message.chat.id
        global user_id
        user_id = id
        bot.send_message(chat_id=message.chat.id, text=f'Your time-zone is set to {time_zone}')
        sched = BlockingScheduler(timezone=pytz.timezone(time_zone))
        sched.add_job(send_words, trigger="cron", hour=9)
        sched.start()
        
    except telebot.apihelper.ApiException as e:
        print(f"Error: {e}")


def send_words():
    current_datetime = datetime.datetime.now()
    day_of_month = current_datetime.day
    daily_word = df["Words"][day_of_month]
    bot.send_message(user_id, f"Hi, this is your daily vocabulary:\n {daily_word}")


bot.polling()