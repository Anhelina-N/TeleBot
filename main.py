import telebot
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
import datetime
import tzlocal
import json

df = pd.read_excel("DailyVocab.xlsx")

bot = telebot.TeleBot('PERSONAL_TOKEN') #Include your personal token here, it can be found in BotFather chat on Telegram
user_data = {}

@bot.message_handler(commands=['start', 'help']) 
def welcomeGetID(message):
    user_id = message.chat.id 
    bot.send_message(message.chat.id, "Hello, this is English Words Bot. I am going to send you vocabulary daily at 8 a.m. your local time to help you improve your English!")
    startPoll(message)

def startPoll(message):
    markup = telebot.types.InlineKeyboardMarkup()
    option1 = telebot.types.InlineKeyboardButton("Beginner", callback_data="Beginner")
    option2 = telebot.types.InlineKeyboardButton("Intermediate", callback_data="Intermediate")
    option3 = telebot.types.InlineKeyboardButton("Advanced", callback_data="Advanced")
    markup.add(option1, option2, option3)
    bot.send_message(message.chat.id, "Please choose your English level:", reply_markup=markup)
    bot.register_next_step_handler(message, englishLevel)

@bot.callback_query_handler(func=lambda call: True)
def englishLevel(call):
    user_data[call.message.chat.id] = {'english_level': call.data}
    user_data[call.message.chat.id]['time_zone'] = str(tzlocal.get_localzone())  # Get the server's timezone
    bot.send_message(call.message.chat.id, f"You have chosen the {call.data} level. You will receive your daily words at 8 a.m. {str(tzlocal.get_localzone())} time-zone")
    scheduleWords(call.message.chat.id)

def scheduleWords(chat_id):
    sched = BlockingScheduler()
    sched.add_job(sendWords, 'cron', hour=8, args=[chat_id], timezone=user_data[chat_id]['time_zone'])  # Scheduled in user's timezone
    sched.start()

def sendWords(chat_id):
    userInfo = user_data.get(chat_id)
    if userInfo:
        englishLevel = userInfo['english_level']
        timeZone = userInfo['time_zone']
        currentDatetime = datetime.datetime.now(pytz.timezone(timeZone))
        day = currentDatetime.day
        dailyWords = df[englishLevel][day]
        bot.send_message(chat_id, f"Hi, these are your daily words! \n\n{dailyWords}")

bot.polling()
