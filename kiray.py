#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
Simple V2Ray FAQ bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import telegram.ext

import logging
import json


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

questions_dict = dict()
text = ''

QUESTION, ANSWER = range(2)

def load_json():
    with open("/root/kiray/save.json","r") as f:
        return json.load(f)

def save_json(dicty):
    with open("/root/kiray/save.json","w") as f:
        json.dump(dicty, f)

def start(bot, update):
    update.message.reply_text(
        '这里是Kiri的V2Ray FAQ bot,用来存档一些常见的问题。你可以：\n '
        '用 /questions 来获取问题列表\n'
        '用 /question <NO.> 来获得对应答案，其中题号是从 /questions 中得到的\n'
        '如果你想添加问题和答案的话，请私戳我（ @kiraybot ）并使用 /add 哟')


def questions(bot,update):
    global text
    update.message.reply_text(text)

def question(bot,update,args):
    global questions_dict
    try:
        choice = str(args[0])
        if choice in questions_dict:
            update.message.reply_text(questions_dict[choice][1])
        else:
            update.message.reply_text("要输入正确的题号哦")
    except (IndexError, ValueError):
        update.message.reply_text("不对不对不对，要输入 /question <No.>")

def add(bot,update):
    global questions_dict
    update.message.reply_text("不要不要不要乱玩bot!并且请确定你是在私聊中使用这个功能。")
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
    update.message.reply_text("好耶！已加入V2RayFAQ全家桶")
    leng = len(questions_dict)
    current = str(leng)
    questions_dict[current].append(update.message.text)
    text = text + str(current) + '.'
    text = text + questions_dict[str(current)][0] + '\n'
    save_json(questions_dict)
    return ConversationHandler.END

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


def main():
    global questions_dict
    global text
    questions_dict = load_json()
    leng = len(questions_dict)
    for key in range(1,leng+1):
        text = text + str(key) + '.'
        text = text + questions_dict[str(key)][0] + '\n'

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(telegram.ext.CommandHandler("start", start))
    dp.add_handler(telegram.ext.CommandHandler("help", start))
    dp.add_handler(telegram.ext.CommandHandler("delete", delete))
    dp.add_handler(telegram.ext.CommandHandler("question", question,
                                               pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler("questions", questions))


    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],

        states={

            QUESTION: [MessageHandler(Filters.text, add_question),
            CommandHandler('cancel', cancel)],

            ANSWER: [MessageHandler(Filters.text, add_answer),
            CommandHandler('cancel', cancel)]
                    
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

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