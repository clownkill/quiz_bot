import json
import logging
import os
from enum import Enum
from functools import partial
from random import choice

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler



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


def handle_new_question_request(update, context, db):
    user = f"user_tg_{update.message.from_user['id']}"
    question_number = choice(db.keys())
    quiz_set = json.loads(db.get(question_number))
    question = quiz_set['question']
    db.set(user, json.dumps({'last_asked_question': question_number}))
    update.message.reply_text(
        question,
        reply_markup=REPLY_MARKUP
    )

    return BotStates.ANSWER.value


def handle_solutions_attempt(update, context, db):
    user = f"user_tg_{update.message.from_user['id']}"
    answer = update.message.text
    last_asked_question = json.loads(db.get(user))['last_asked_question']
    correct_answer = json.loads(db.get(last_asked_question))['answer']

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


def handle_give_up(update, context, db):
    user = f"user_tg_{update.message.from_user['id']}"
    last_asked_question = json.loads(db.get(user))['last_asked_question']
    correct_answer = json.loads(db.get(last_asked_question))['answer']

    update.message.reply_text(
        f'''Правильный ответ:
        {correct_answer}
        ''',
        reply_markup=REPLY_MARKUP
    )

    handle_new_question_request(update, context, db)


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

    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=(os.getenv('REDIS_PORT')),
        decode_responses=True,
        password=os.getenv('REDIS_PASSWORD')
    )


    updater = Updater(tg_quiz_bot_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotStates.QUESTION.value: [
                MessageHandler(Filters.regex('^Новый вопрос$'), partial(handle_new_question_request, db=db))
            ],
            BotStates.ANSWER.value: [
                MessageHandler(Filters.regex('^Сдаться$'), partial(handle_give_up, db=db)),
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
