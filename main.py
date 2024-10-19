import telegram
from environs import Env
import requests

from datetime import datetime
import asyncio
import time
import logging

from bot_logging import setup_logger


def generate_message(new_attempt):
    lesson_title = new_attempt['lesson_title']
    message = f'У вас проверили работу "{lesson_title}"'
    message += '\n'
    if new_attempt['is_negative']:
        message += 'К сожалению, в работе нашлись ошибки.'
    else:
        message += 'Преподавателю всё понравилось, можете приступать к следующему уроку!'  # noqa: E501
    message += '\n'
    message += new_attempt['lesson_url']
    return message


async def send_messages(bot, chat_id_tg, new_attempts):
    for new_attempt in new_attempts:
        async with bot:
            await bot.send_message(
                chat_id=chat_id_tg,
                text=generate_message(new_attempt)
            )


def check_response(response):
    if not response.get('status'):
        return None
    if not response.get('new_attempts'):
        return None
    return True


def start_main_bot(chat_id_tg, bot, auth_header):
    timestamp_to_request = None
    while (True):
        response = fetch_attempts_with_retries(
            auth_header, timestamp_to_request
        )
        if not response:
            continue
        response = response.json()
        is_new_messages = check_response(response)
        timestamp_to_request = (
            response.get('timestamp_to_request') or
            response.get('last_attempt_timestamp')
        )
        if is_new_messages:
            new_attempts = response['new_attempts']
            asyncio.run(send_messages(bot, chat_id_tg, new_attempts))


def fetch_attempts_with_retries(auth_header, timestamp_to_request):  # noqa: E501
    params = {
        'timestamp': timestamp_to_request or datetime.now().timestamp()
    }
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(url, headers=auth_header, params=params)
    response.raise_for_status()
    return response


def exception_out(text, exception, bot, chat_id):
    logging.error(f'{text}: {exception}', exc_info=True)
    time.sleep(4)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_chat_id = env.str('TELEGRAM_CHAT_ID')
    main_bot = telegram.Bot(token=env.str('TELEGRAM_MAIN_BOT_TOKEN'))
    logger_bot = telegram.Bot(token=env.str('TELEGRAM_LOGGER_BOT_TOKEN'))
    setup_logger(logger_bot, tg_chat_id)
    dvmn_token = env.str('DEVMAN_TOKEN')
    auth_header = {'Authorization': f'Token {dvmn_token}'}
    logging.info('Кажется, основной бот запустился.')
    while (True):
        try:
            start_main_bot(tg_chat_id, main_bot, auth_header)
        except (requests.ConnectionError) as e:
            exception_out(
                'Ошибка ConnectionError: ', e, logger_bot, tg_chat_id
            )
        except (requests.exceptions.ReadTimeout) as e:
            exception_out(
                'Ошибка ReadTimeout: ', e, logger_bot, tg_chat_id
            )
        except requests.exceptions.HTTPError as e:
            exception_out(
                'Ошибка HTTPerror', e, logger_bot, tg_chat_id
            )
        except Exception as e:
            exception_out(
                'Шеф, у нас неожиданная ошибка: ', e, logger_bot, tg_chat_id
            )
