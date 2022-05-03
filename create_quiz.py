import json
import os

import redis
from dotenv import load_dotenv


def create_quiz(quiz_dir, db):
    files = os.listdir(quiz_dir)
    quiz = {}

    for file_name in files:
        file = os.path.join(quiz_dir, file_name)
        with open(file, 'r', encoding='KOI8-R') as f:
            text = f.read()

        text_parts = text.split('\n\n')

        questions = []
        answers = []

        for part in text_parts:
            if 'Вопрос' in part:
                questions.append(part)
            elif 'Ответ' in part:
                answers.append(part)

        clear_questions = [' '.join(question.split(':')[1:]).strip() for question in questions]

        clear_answers = []
        for answer in answers:
            splited_answer = answer.split('\n')[1]
            if '.' in splited_answer:
                sanitize_answer = splited_answer.split('.')[0].strip()
                if '(' in sanitize_answer:
                    sanitize_answer = sanitize_answer.split('(')[0].strip()
                clear_answers.append(sanitize_answer)
            elif '(' in splited_answer:
                sanitize_answer = splited_answer.split('(')[0].strip()
                clear_answers.append(sanitize_answer)
            else:
                clear_answers.append(splited_answer)

        quiz.update(dict(zip(clear_questions, clear_answers)))

    counter = 1
    while counter < len(quiz):
        for question, answer in quiz.items():
            if answer and question:
                quiz_set = {
                    'question': question,
                    'answer': answer
                }
                db.set(f'question_{counter}', json.dumps(quiz_set))
                print(f'added quiz_set {counter}')
            counter += 1

    return len(quiz)


if __name__ == '__main__':
    load_dotenv()
    quiz_dir = os.getenv('QUIZ_DIR')

    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=(os.getenv('REDIS_PORT')),
        decode_responses=True,
        password=os.getenv('REDIS_PASSWORD')
    )

    quiz = create_quiz(quiz_dir, db)
    print(quiz)
