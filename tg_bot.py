import logging
import os
import random

import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from create_quiz import create_quiz


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_question_answer():
    quiz_file = 'temp/1vs1200.txt'
    quiz = create_quiz(quiz_file)
    question_and_answer = random.sample(quiz, 1)[0]
    question = question_and_answer['question']
    answer = question_and_answer['answer']

    return question, answer


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


def check_user_input(bot, update):
    if update.message.text == 'Новый вопрос':
        question, answer = get_question_answer()
        send_question(bot, update, question)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    tg_quiz_bot_token = os.getenv('TG_QUIZ_BOT_TOKEN')

    updater = Updater(tg_quiz_bot_token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, check_user_input))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
