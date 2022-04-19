import logging
import os
from enum import Enum
from functools import partial
from random import choice

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from create_quiz import create_quiz


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BotStates = Enum('BotStates', 'ANSWER QUESTION')

REPLY_KEYBOARD = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
REPLY_MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD, one_time_keyboard=True)

def start(update, context):
    update.message.reply_text(
        text='Привет! Я бот для викторин!',
        reply_markup=REPLY_MARKUP
    )

    return BotStates.QUESTION.value


def handle_new_question_request(update, context, db, quiz):
    user = update.message.from_user['id']
    question = choice(list(quiz.keys()))
    answer = quiz[question]
    print(answer)
    db.set(user, answer)
    update.message.reply_text(
        question,
        reply_markup=REPLY_MARKUP
    )

    return BotStates.ANSWER.value


def handle_solutions_attempt(update, context, db):
    user = update.message.from_user['id']
    answer = update.message.text
    correct_answer = db.get(user)

    if answer.lower() == correct_answer.lower():
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".',
            reply_markup=REPLY_MARKUP
        )
        return BotStates.QUESTION.value
    else:
        update.message.reply_text(
            'Неправильно...Попробуй еще раз',
            reply_markup=REPLY_MARKUP
        )
        return BotStates.ANSWER.value


def handle_give_up(update, context, db, quiz):
    user = update.message.from_user['id']
    answer = db.get(user)

    update.message.reply_text(
        f'''Правильный ответ:
        {answer}
        ''',
        reply_markup=REPLY_MARKUP
    )

    handle_new_question_request(update, context, db, quiz)


def done(update, context):
    user_data = context.user_data

    update.message.reply_text(
        'Ждем Вас снова в нашей викторине!',
        reply_markup=ReplyKeyboardRemove()
    )

    user_data.clear()
    return ConversationHandler.END


def error(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    tg_quiz_bot_token = os.getenv('TG_QUIZ_BOT_TOKEN')
    quiz_dir = os.getenv('QUIZ_DIR')

    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=(os.getenv('REDIS_PORT')),
        decode_responses=True,
        password=os.getenv('REDIS_PASSWORD')
    )

    quiz = create_quiz(quiz_dir)

    updater = Updater(tg_quiz_bot_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotStates.QUESTION.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), partial(handle_new_question_request, db=db, quiz=quiz))
            ],
            BotStates.ANSWER.value: [
                MessageHandler(Filters.regex('^Сдаться$'), partial(handle_give_up, db=db, quiz=quiz)),
                MessageHandler(Filters.text, partial(handle_solutions_attempt, db=db)),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
