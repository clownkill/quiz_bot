import logging
import os
from random import choice

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from create_quiz import create_quiz


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv()
TG_QUIZ_BOT_TOKEN = os.getenv('TG_QUIZ_BOT_TOKEN')
DB = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=(os.getenv('REDIS_PORT')),
    db=0,
    decode_responses=True,
    # password=os.getenv('REDIS_PASSWORD')
)


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text(
        text='Привет! Я бот для викторин!',
        reply_markup=reply_markup
    )


def send_question(bot, update, question):
    update.message.reply_text(question)


def check_user_answer(bot, update, user_id):
    question = DB.get(user_id)
    answer = DB.get(question)
    user_answer = update.message.text
    if user_answer.lower() == answer.lower():
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
    else:
        update.message.reply_text('Неправльно... Попробуете еще раз?')


def check_user_input(bot, update):
    user_id = update.message.from_user['id']
    quiz = create_quiz()
    questions = list(quiz.keys())
    if update.message.text == 'Новый вопрос':
        question = choice(questions)
        answer = quiz[question]
        print(answer)
        DB.set(user_id, question)
        DB.set(question, answer)
        send_question(bot, update, question)
    if update.message.text == 'Сдаться':
        question = DB.get(user_id)
        answer = DB.get(question)
        send_question(bot, update, answer)
    else:
        check_user_answer(bot, update, user_id)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TG_QUIZ_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, check_user_input))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
