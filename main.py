def get_question_file(file):
    with open(file, 'r', encoding='koi8-r') as file:
        file_questions = file.read()

    print(file_questions)


def main():
    file = 'temp/1vs1200.txt'
    get_question_file(file)


if __name__ == '__main__':
    main()