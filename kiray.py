#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import telegram.ext

import logging
import json
from time import time


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

questions_dict = dict()
text = ''
No = '0'

QUESTION, ANSWER = range(2)
EDIT_QUESTION, EDIT_ANSWER = range(2)


def load_json():
    with open("/root/kiray/save.json","r") as f:
        return json.load(f)


def save_json(dicty):
    myjsondump = json.dumps(dicty, indent=1)
    with open("/root/kiray/save.json","w") as f:
        f.writelines(myjsondump)


def generate_text():
    text = ''
    questions_dict = load_json()
    leng = len(questions_dict)
    for key in range(1,leng+1):
        text = text + str(key) + '.'
        text = text + questions_dict[str(key)][0] + '\n'
    return text


def start(bot, update):
    update.message.reply_text(
        '这里是Kiri的V2Ray FAQ bot,用来存档一些常见的问题。你可以：\n '
        '用 /questions 来获取问题列表\n'
        '用 /answer <NO.> 来获得对应答案，其中题号是从 /questions 中得到的\n'
        '如果你想添加问题和答案的话，请私戳我（ @kiraybot ）并使用 /add 哟')


def questions(bot,update,chat_data):
    global text
    current_time = time()
    chat_id = update.message.chat_id
    if chat_id < 0:
        if chat_id in chat_data:
            delta = int(current_time - chat_data[chat_id])
        else:
            update.message.reply_text(text)
            chat_data[chat_id] = current_time
            return

        if delta < 300:
            remain = 300 -delta
            update.message.reply_text("不要刷屏啦！过{}分{}秒再来！不然小心被滥权哟～".format(int(remain/60),remain%60))
        else:
            update.message.reply_text(text)
            chat_data[chat_id] = current_time

    else:
        update.message.reply_text(text)


def question(bot,update,args):
    global questions_dict
    try:
        choice = str(args[0])
        if choice in questions_dict:
            update.message.reply_text(questions_dict[choice][1])
            update.message.reply_text("另外，因为少个s很多视力不好的人看不出来，以后就用 /answer 来查答案啦～")
        else:
            update.message.reply_text("要输入正确的题号哦")
    except (IndexError, ValueError):
        update.message.reply_text("不对不对不对，要输入 /answer <No.>(因为你们老看错，所以question就弃用啦)")


def answer(bot,update,args):
    global questions_dict
    try:
        choice = str(args[0])
        if choice in questions_dict:
            update.message.reply_text(questions_dict[choice][1])
        else:
            update.message.reply_text("要输入正确的题号哦")
    except (IndexError, ValueError):
        update.message.reply_text("不对不对不对，要输入 /answer <No.>")


def edit(bot,update,args):
    global questions_dict
    global text
    global No
    try:
        question_num = str(args[0])
        if question_num not in questions_dict:
            update.message.reply_text("这里没有你想编辑的题！")
            return ConversationHandler.END
        No = question_num
        q_or_a = int(args[1])
        if q_or_a == 0:
            update.message.reply_text("现在开始编辑第{}道题的问题".format(question_num))
            return EDIT_QUESTION
        elif q_or_a == 1:
            update.message.reply_text("现在开始编辑第{}道题的答案".format(question_num))
            return EDIT_ANSWER
        else :
            update.message.reply_text("0代表问题，1代表答案！")
            return ConversationHandler.END
    except (KeyError, IndexError, ValueError):
        update.message.reply_text("不对不对不对，要输入 /edit <No.> [0,1]")
        return ConversationHandler.END


def edit_question(bot,update):
    global questions_dict
    global No
    global text
    questions_dict[No][0] = update.message.text
    save_json(questions_dict)
    update.message.reply_text("好耶！你已修改第{}题的问题为\n{}".format(No, update.message.text))
    text = generate_text()
    return ConversationHandler.END


def edit_answer(bot,update):
    global questions_dict
    global No
    global text
    questions_dict[No][1] = update.message.text
    save_json(questions_dict)
    update.message.reply_text("好耶！你已修改第{}题的答案为\n{}".format(No, update.message.text))
    text = generate_text()
    return ConversationHandler.END


def add(bot,update):
    global questions_dict
    chat_id = update.message.chat_id
    if chat_id < 0:
        update.message.reply_text("就说了要在私戳的时候用 /add 啦！")
        return ConversationHandler.END
    update.message.reply_text("不要不要不要乱玩bot!（小心被滥权哟）并且请确定你是在私聊中使用这个功能。")
    update.message.reply_text("那我们开始吧。输入你想放入的问题，尽量短一点。如果你是不小心按到，请输入 /cancel")
    leng = str(len(questions_dict))
    if len(questions_dict[leng]) != 2:
        del questions_dict[leng]
    return QUESTION


def add_question(bot,update):
    global questions_dict
    update.message.reply_text("好耶。继续输入你想放入的答案，一口气地。 如果你是不小心按到，请输入 /cancel")
    leng = len(questions_dict)
    current = str(leng+1)
    questions_dict[current] = []
    questions_dict[current].append(update.message.text)
    return ANSWER


def add_answer(bot,update):
    global questions_dict
    global text
    username = update.message.from_user.username
    shuiid = -1001108895871
    update.message.reply_text("好耶！已加入V2RayFAQ全家桶")
    leng = len(questions_dict)
    current = str(leng)
    questions_dict[current].append(update.message.text)
    text = text + str(current) + '.'
    text = text + questions_dict[str(current)][0] + '\n'
    save_json(questions_dict)
    if username == None :
        try:
            username = update.message.from_user.first_name + update.message.from_user.last_name
        except(TypeError):
            username = update.message.from_user.first_name
    little_report = '''就是这个人 @{} 刚刚提交了问题
    {}.{}
    答: {}'''.format(username, current, questions_dict[current][0], questions_dict[current][1])
    bot.send_message(shuiid, text=little_report)


    return ConversationHandler.END


def search(bot,update,args):
    global questions_dict


def delete(bot,update):
    global questions_dict
    global text
    user = update.message.from_user.first_name
    if user != 'Kiri':
        update.message.reply_text("别尼玛乱玩bot啦！")
    else:
        leng = len(questions_dict)
        del questions_dict[str(leng)]
        update.message.reply_text("删除成功惹！")
        save_json(questions_dict)
        text = ''
        leng = len(questions_dict)
        for key in range(1,leng+1):
            text = text + str(key) + '.'
            text = text + questions_dict[str(key)][0] + '\n'


def cancel(bot, update):
    global questions_dict
    update.message.reply_text('好啦，那就下次再见咯。',
                              reply_markup=ReplyKeyboardRemove())
    leng = str(len(questions_dict))
    if len(questions_dict[leng]) != 2:
        del questions_dict[leng]
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def get_chatid(bot,update):
    update.message.reply_text(update.message.chat_id)


#def get_username(bot,update):
#    update.message.reply_text(update.message.from_user.username)


def main():
    global questions_dict
    global text
    questions_dict = load_json()
    text = generate_text()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(telegram.ext.CommandHandler("start", start))
    dp.add_handler(telegram.ext.CommandHandler("help", start))
    dp.add_handler(telegram.ext.CommandHandler("delete", delete))
    dp.add_handler(telegram.ext.CommandHandler("get_chatid", get_chatid))
#   dp.add_handler(telegram.ext.CommandHandler("get_username", get_username))
    dp.add_handler(telegram.ext.CommandHandler("question", question,
                                               pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler("answer", answer,
                                               pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler("questions", questions,
                                                pass_chat_data=True))


    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('add', add)],

        states={

            QUESTION: [MessageHandler(Filters.text, add_question),
            CommandHandler('cancel', cancel)],

            ANSWER: [MessageHandler(Filters.text, add_answer),
            CommandHandler('cancel', cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('edit', edit, pass_args=True)],

        states={

            EDIT_QUESTION: [MessageHandler(Filters.text, edit_question),
            CommandHandler('cancel', cancel)],

            EDIT_ANSWER: [MessageHandler(Filters.text, edit_answer),
            CommandHandler('cancel', cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler1)

    dp.add_handler(conv_handler2)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
