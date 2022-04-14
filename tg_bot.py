import logging
import os
import random

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
    password=os.getenv('REDIS_PASSWORD')
)


def get_question_card():
    quiz = create_quiz()
    question_card = random.sample(quiz, 1)[0]
    # question = question_card['question']
    # answer = question_card['answer']

    return question_card


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
    if update.message.text == DB.get(user_id):
        print(DB.get(user_id))
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
    else:
        print(DB.get(user_id))
        update.message.reply_text('Неправльно... Попробуете еще раз?')


def check_user_input(bot, update):
    user_id = update.message.from_user['id']
    if update.message.text == 'Новый вопрос':
        question_card = get_question_card()
        question = question_card['question']
        DB.set(user_id, question_card['answer'])
        send_question(bot, update, question)
    if update.message.text == 'Сдаться':
        answer = DB.get(user_id)
        send_question(bot, update, answer)
    if not update.message.text.startswith('Вопрос'):
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
