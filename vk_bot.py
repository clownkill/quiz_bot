import os
from random import choice

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from create_quiz import create_quiz


def send_new_question(event, vk_api, keyboard, db, quiz):
    user_id = event.user_id
    question = choice(list(quiz.keys()))
    answer = quiz[question]
    db.set(user_id, question)
    db.set(question, answer)

    vk_api.messages.send(
        user_id=user_id,
        message=question,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def hand_up(event, vk_api, keyboard, db):
    user_id = event.user_id
    question = db.get(user_id)
    answer = db.get(question)
    message = f'''Правильный ответ:
    {answer}'''

    vk_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def check_solutions_attempt(event, vk_api, keyboard, db):
    user_id = event.user_id
    question = db.get(user_id)
    answer = db.get(question)
    user_answer = event.text
    if user_answer.lower() == answer.lower:
        vk_api.messages.send(
            user_id=user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            user_id=user_id,
            message='Неправильно...Попробуй еще раз',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )


def main():
    load_dotenv()
    vk_quiz_bot_token = os.getenv('VK_QUIZ_BOT_TOKEN')

    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=(os.getenv('REDIS_PORT')),
        decode_responses=True,
        password=os.getenv('REDIS_PASSWORD')
    )

    quiz = create_quiz()

    vk_session = vk.VkApi(token=vk_quiz_bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                send_new_question(event, vk_api, keyboard, db, quiz)
            elif event.text == 'Сдаться':
                hand_up(event, vk_api, keyboard, db)
            else:
                check_solutions_attempt(event, vk_api, keyboard, db)


if __name__ == '__main__':
    main()
