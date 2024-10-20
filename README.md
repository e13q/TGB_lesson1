
# Отправляем уведомления о проверке работ 

В данном проекте реализован телеграмм-бот для получения информации о проверке заданий на [devman](https://dvmn.org) с помощью [API devman](https://dvmn.org/api/docs/)

### Как установить

Python3 должен быть установлен. 
Используйте `pip` для установки зависимостей:
```
pip install -r requirements.txt
```

Для взаимодействия с [API devman](https://dvmn.org/api/docs/) необходим токен. Получить токен можно, ознакомившись с разделом "Аутентификация" в [статье](https://dvmn.org/api/docs/).

Также, нужно 2 токена телеграмм ботов. Один для основной работы, второй для логирования.
[Инструкция по созданию бота](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram.html).

И не забудьте про ID чата, получить который можно написав на [@userinfobot](https://t.me/userinfobot) пункт "id".

После получения всего необходимо создать в корневой папке проекта файл .env и добавить значения: 

```
DEVMAN_TOKEN = 'Ваш токен'
TELEGRAM_MAIN_BOT_TOKEN = 'Ваш токен основного бота'
TELEGRAM_LOGGER_BOT_TOKEN = 'Ваш токен бота для логирования'
TELEGRAM_CHAT_ID = 'Ваш id'
```

Запустить скрипт можно выполнив команду:

`python3 main.py`

### Пример работы скрипта

![image](https://github.com/user-attachments/assets/7f8f6f5c-86eb-4166-8baa-daff98a67aeb)

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
