import os
from random import choice

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.getenv('BASE_DIR')


def get_rnd_quiz_file():
    file_name = choice(os.listdir(BASE_DIR))
    file = os.path.join(BASE_DIR, file_name)

    return file


def create_quiz():
    file = get_rnd_quiz_file()

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

    quiz = dict(zip(clear_questions, clear_answers))

    return quiz

if __name__ == '__main__':
    quiz = create_quiz()
    print(quiz)
