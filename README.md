# quiz_bot
 
Боты для проведения викторины в Telegram(@quizdvmnbot) и [Вконтакте](https://vk.com/club212748781)

## Как установить

* Python3 должен быть установлен
* Скопировать репозиторий к себе на компьютер:
```
https://github.com/clownkill/quiz_bot
```
* Установите зависимости:
```
pip install -r requrirements
```

## Переменные окружения

```
VK_QUIZ_BOT_TOKEN=[VK-токен для доступа к сообществу]
TG_QUIZ_BOT_TOKEN=[Telegram-токен для достуба к боту]
REDIS_HOST=[Хост для базы данных Redix]
REDIS_PORT=[Порт базы данных Redis]
REDIS_DB_PSWD=[Пароль к базе данных Redis]
BASE_DIR=[путь к каталогу в котором хранятся файлы с вопросами и ответами для викторины]
```

## Как запустить

* Для запуска telegram-бота необходимо выполнить:
```
python tg_bot.py
```
* Для запуска vk-бота необходимо выполнить:
```
python vk_bot.py
```

## Деплой

Для деплоя проекта необходимо воспользоваться инструкцией на [heroku](https://devcenter.heroku.com/categories/deployment).

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org).