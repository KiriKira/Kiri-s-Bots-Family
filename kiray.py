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

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,
                      InlineKeyboardMarkup, error)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
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
        '用 /questions 来获取问题列表（翻页模式）\n'
        '用 /all_questions 来获取全部问题（请在私聊中使用）\n'
        '用 /answer <NO.> 来获得对应答案，其中题号是从 /questions 中得到的\n'
        '如果你想添加问题和答案的话，请私戳我（ @kiraybot ）并使用 /add 哟\n')


def all_questions(bot,update,chat_data):
    global text
    chat_id = update.message.chat_id
    if chat_id < 0:
        update.message.reply_text("为了防止刷屏，请在私戳中查看哟")
    else:
        update.message.reply_text(text)


def questions(bot,update,chat_data):
    global questions_dict
    current_time = time()
    chat_id = update.message.chat_id
    keyboard = [[InlineKeyboardButton("Next", callback_data='2')],
               [InlineKeyboardButton(str(i), callback_data=str(i+2)) for i in range(1,6)]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    reply_text = ''
    for i in range(1,6):
        reply_text += "{}.{}\n".format(str(i), questions_dict[str(i)][0])

    if chat_id < 0:
        if chat_id in chat_data:
            delta = int(current_time - chat_data[chat_id])
        else:
            update.message.reply_text(reply_text, reply_markup=reply_markup)
            chat_data[chat_id] = current_time
            chat_data[int(chat_id) + 10086] = 1
            return

        if delta < 300:
            return
        else:
            update.message.reply_text(reply_text, reply_markup=reply_markup)
            chat_data[chat_id] = current_time
            chat_data[int(chat_id) + 10086] = 1

    else:
        update.message.reply_text(reply_text, reply_markup=reply_markup)
        chat_data[int(chat_id) + 10086] = 1


def button(bot, update, chat_data):
    """

    :param bot: bot itself
    :param update: updated message
    :param chat_data: chat_data[chat_id] is the time of last call of function , while chat_data[chat_id + 10086] is the
    status of current number of question.
    :return: None
    """

    global questions_dict
    query = update.callback_query
    choice = query.data
    chat_id = query.message.chat_id
    uid = query.from_user.id
    mid = query.message.message_id
    current_time = time()

    if chat_id not in chat_data or (chat_id + 10086) not in chat_data:
        chat_data[chat_id + 10086] = 1
    qid = int(chat_id) + 10086
    chat_data[chat_id] = current_time

    if choice == '1' and chat_data[qid] >= 6:
        chat_data[qid] -= 5
    elif choice == '2' and chat_data[qid] <= (len(questions_dict) - 5):
        chat_data[qid] += 5
    elif choice == '1' or choice == '2':
        chat_data[qid] = 1
    else:
        choice = int(choice) - 2
        reply_text = "[{}](tg://user?id={})这是你想看哒\n{}.{}\n答:{}".format(
                query.from_user.first_name,
                query.from_user.id,
                choice, questions_dict[str(choice)][0],
                questions_dict[str(choice)][1])

        if (uid, mid) in chat_data:
            try:
                chat_data[(uid, mid)].edit_text(text=reply_text, parse_mode='Markdown')
            except[error.BadRequest, error.NetworkError]:
                reply_text = "{}.{}\n答:{}".format(choice, questions_dict[str(choice)][0],
                                                  questions_dict[str(choice)][1])
                chat_data[(uid, mid)].edit_text(text=reply_text)
            query.answer()
            return
        archive = bot.send_message(chat_id, text=reply_text, parse_mode='Markdown')
        chat_data[(uid, mid)] = archive

        query.answer()
        return

    current = chat_data[qid]
    edited_text = ''
    for i in range(current, min(current+5,len(questions_dict)+1)):
        edited_text += "{}.{}\n".format(i, questions_dict[str(i)][0])
    questions_keyboard = [[InlineKeyboardButton(str(i), callback_data=str(i + 2))
                          for i in range(current, min(current+5,len(questions_dict)+1))]]

    if chat_data[qid] <= 5:
        keyboard = [[InlineKeyboardButton("Next", callback_data='2')]] + questions_keyboard
    elif chat_data[qid] >= (len(questions_dict) -4):
        keyboard = [[InlineKeyboardButton("Previous", callback_data='1')]] + questions_keyboard
    else:
        keyboard = [[InlineKeyboardButton("Previous", callback_data='1'),
                     InlineKeyboardButton("Next", callback_data='2')]] + questions_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.edit_message_text(text=edited_text,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=reply_markup)
    query.answer()


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
            reply_text = '问：{}\n答：{}'.format(questions_dict[choice][0], questions_dict[choice][1])
            try:
                update.message.reply_text(reply_text, parse_mode='Markdown')
            except[error.BadRequest, error.NetworkError]:
                update.message.reply_text(reply_text)
        else:
            update.message.reply_text("要输入正确的题号哦")
    except (IndexError, ValueError):
        return


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
    update.message.reply_text("不要不要不要乱玩bot!（小心被滥权哟）并且注意当你使用Markdown模式时，"
                              "bot收到的是渲染之后的文本，Markdown记号跟渲染效果都会被tg抹去再由bot接收。")
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
    username = update.message.from_user.first_name
    uid = update.message.from_user.id
    shuiid = -1001108895871
    update.message.reply_text("好耶！已加入V2RayFAQ全家桶")
    leng = len(questions_dict)
    current = str(leng)
    questions_dict[current].append(update.message.text)
    text = text + str(current) + '.'
    text = text + questions_dict[str(current)][0] + '\n'
    save_json(questions_dict)
    little_report = '''就是这个人 [{}](tg://user?id={}) 刚刚提交了问题
    {}.{}
    答: {}'''.format(username, uid, current, questions_dict[current][0], questions_dict[current][1])
    bot.send_message(shuiid, text=little_report, parse_mode='Markdown')

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

def get_username(bot,update):
    update.message.reply_text(update.message.from_user.username)

def main():
    global questions_dict
    global text
    questions_dict = load_json()
    text = generate_text()

    updater = Updater("TOKEN")

    dp = updater.dispatcher

    dp.add_handler(telegram.ext.CommandHandler("start", start))
    dp.add_handler(telegram.ext.CommandHandler("help", start))
    dp.add_handler(telegram.ext.CommandHandler("delete", delete))
    dp.add_handler(telegram.ext.CommandHandler("get_chatid", get_chatid))
    dp.add_handler(telegram.ext.CommandHandler("get_username", get_username))
    dp.add_handler(telegram.ext.CommandHandler("question", question,
                                               pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler("answer", answer,
                                               pass_args=True))
    dp.add_handler(telegram.ext.CommandHandler("all_questions", all_questions,
                                                pass_chat_data=True))
    dp.add_handler(CommandHandler('questions', questions,
                                  pass_chat_data=True))
    dp.add_handler(CallbackQueryHandler(button, pass_chat_data=True))


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
