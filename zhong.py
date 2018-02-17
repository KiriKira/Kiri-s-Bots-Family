#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Simple Bot to send timed Telegram messages.
# This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import telegram.ext
import logging
import random
import re
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('''用 /set <second>来设置钟声响起的间隔
用 /setp <second> text 来设置多少秒后钟要说什么
用 /unset 来取消使用/set 设置的钟钟
还有 /shutup 这会把所有的钟钟都关掉''')


def alarm(bot, job):
    """Send the alarm message."""
    num = job.context[1] % 12 + 1
    job.context[1] += 1
    text=num * '铛'
    bot.send_message(job.context[0], text)


def alarmp(bot, job):
    text = job.context[1]
    bot.send_message(job.context[0], text=text)


def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    user = update.message.from_user.first_name
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        date_now = datetime.datetime.now()
        date_target = date_now

        if len(args) == 2:
            date_target_str = str(args[1])
            if re.match(r"\d\d[:：]\d\d[：:]\d\d",date_target_str):
                hour, minute, second = re.split(r"[:：]",date_target_str)
                if (0 <= int(hour) <= 23) and  (0 <= int(minute) <= 59) and (0 <= int(second) <=59):
                    date_target = datetime.datetime(date_now.year,date_now.month,date_now.day,
                                                    int(hour),int(minute),int(second))
                    if date_target <= date_now:
                        date_target = date_target + datetime.timedelta(days=1)
                else:
                    update.message.reply_text("乱打时间的人钟钟可不能原谅！")
                    return
            else:
                update.message.reply_text("正确的格式应该是 /set 3600 00:00:00 辣！")
                return

        if due < 0:
            update.message.reply_text('时间倒流是只有长者才能办到的事！!')
            return
        elif due <60:
            update.message.reply_text('不要搞事啦，小心被滥权哦！才{}秒就要敲一次，你想累死钟钟吗？'.format(str(due)))
            return
        
        if user in chat_data :
            update.message.reply_text('一人只能用一个钟钟的啦！')
            return

        # Add job to queue
        chat_num = 0
        job = job_queue.run_repeating(alarm, interval=due,first=date_target, context=[chat_id, chat_num])
        chat_data[user] = job

        update.message.reply_text('成功设置啦！好孩子会在设错的时候用 /unset 取消的！')
    except (IndexError, ValueError):
        update.message.reply_text('/set 3600 要像这样用哟！')


def set_timer_personal(bot, update, args, job_queue, chat_data):
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        text = update.message.text.split(' ',2)[2]
        if text == '':
            raise IndexError("list index out of range")
        if due < 0:
            update.message.reply_text('时间倒流是只有长者才能办到的事！!')
            return

        # Add job to queue
        job = job_queue.run_once(alarmp, due, context=[chat_id, text])


    except (IndexError, ValueError):
        update.message.reply_text('/setp 5 浪姐女装 \n要像这样用哟！')


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    user = update.message.from_user.first_name
    if user not in chat_data:
        update.message.reply_text('还没有属于你的钟钟哟')
        return

    job = chat_data[user]
    job.schedule_removal()
    del chat_data[user]

    update.message.reply_text('关掉你的钟啦！')

def shutup(bot, update, chat_data):
    for key in list(chat_data) :
        job = chat_data[key]
        job.schedule_removal()
        del chat_data[key]
    
    update.message.reply_text('钟钟闭嘴就是了嘛，哼')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def welcome(bot,update):
    welcome_msg = ['有新大佬来了',
                   '有奇怪的东西进来了',
                   '啊啊啊不能进来啊，这么多一起进来的话。。',
                   '这里是正规群，不女装的请退群',
                   '这里是正规群，不退群的请女装',
                   '这里是正规群，不女装的请让群主女装']

    if(update.message.new_chat_members):
        chat_id = update.message.chat.id
        message_rnd = random.choice(welcome_msg)
        bot.sendMessage(chat_id=chat_id, text=message_rnd)

def fuq(bot,update):
    welcome_msg = ['有新大佬来了',
                   '有奇怪的东西进来了',
                   '啊啊啊不能进来啊，这么多一起进来的话。。',
                   '这里是正规群，不女装的请退群',
                   '这里是正规群，不退群的请女装',
                   '这里是正规群，不女装的请让群主女装']

    reply_msg = ['二五崽不要学钟钟说话！',
                 'Fa♂Q,学钟钟说话是会被续掉的哟',
                 '你是想跟我一起变成魔法少女吗？',
                 '好啦好啦小裙子给你，别再学钟钟啦！',
                 '这么喜欢钟钟的话。。。把你许配给Kiri也不是不可以啦']
    text = update.message.text
    if text in welcome_msg or text in reply_msg:
        update.message.reply_text(random.choice(reply_msg))

    if re.match("[亲,抱]+.*[rgy,饶耕宇].*", text) or re.match(".*[rgy,饶耕宇].*[亲,抱,啪啪啪]+.*", text):
        if random.choice(range(2)) == 1:
            re_list = ["那么喜欢的话……钟钟就把rgy给你啦~",
                  "亲亲rgy",
                  "No gay, plz!",
                  "More gay, plz!"]
            update.message.reply_text(random.choice(re_list))

def main():
    """Run bot."""
    updater = telegram.ext.Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(telegram.ext.CommandHandler("start", start))
    dp.add_handler(telegram.ext.CommandHandler("help", start))
    dp.add_handler(telegram.ext.CommandHandler("set", set_timer,
                                               pass_args=True,
                                               pass_job_queue=True,
                                               pass_chat_data=True))
    dp.add_handler(telegram.ext.CommandHandler("setp", set_timer_personal,
                                               pass_args=True,
                                               pass_job_queue=True,
                                               pass_chat_data=True))
    dp.add_handler(telegram.ext.CommandHandler("unset", unset, pass_chat_data=True))
    dp.add_handler(telegram.ext.CommandHandler("shutup", shutup, pass_chat_data=True))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.status_update, welcome))
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, fuq))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
