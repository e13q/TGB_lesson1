import telegram
from environs import Env
import requests

from datetime import datetime
import asyncio
import time


def generate_message(new_attempt):
    message = f'У вас проверили работу "{new_attempt['lesson_title']}"'
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


def start_bot(chat_id_tg, token_bot_tg, auth_header):
    bot = telegram.Bot(token=token_bot_tg)
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


def fetch_attempts_with_retries(auth_header, timestamp_to_request, retries=3, delay=4):  # noqa: E501
    for connection_try in range(retries):
        try:
            params = {
                'timestamp': timestamp_to_request or datetime.now().timestamp()
            }
            url = 'https://dvmn.org/api/long_polling/'
            response = requests.get(url, headers=auth_header, params=params)
            response.raise_for_status()
            return response
        except (requests.ConnectionError):
            print(
                f'An attempt to connect {connection_try + 1} of {retries} failed'  # noqa: E501
            )
            if connection_try < retries - 1:
                time.sleep(delay)
            else:
                print('All attempts have been exhausted.')
                return None
        except (requests.exceptions.ReadTimeout) as e:
            print(f'ReadTimeout {e}')
            return None
        except requests.exceptions.HTTPError as e:
            print(f'HTTPerror {e}')
            return None
        except requests.RequestException as e:
            print(f'Request exception: {e}')
            return None


if __name__ == '__main__':
    env = Env()
    env.read_env()
    tg_chat_id = env.str('TELEGRAM_CHAT_ID')
    bot_tg_token = env.str('TELEGRAM_BOT_TOKEN')
    dvmn_token = env.str('DEVMAN_TOKEN')
    auth_header = {'Authorization': f'Token {dvmn_token}'}
    start_bot(tg_chat_id, bot_tg_token, auth_header)
