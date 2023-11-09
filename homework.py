import logging
import os
import datetime
import time
import telegram
import requests
import exceptions

from http import HTTPStatus

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def check_tokens():
    '''Проверка наличия токенов'''
    no_tokens_message = ('Отсутствует переменная окружения:')
    tokens_bool = True
    if PRACTICUM_TOKEN is None:
        tokens_bool = False
        logger.critical(f'{no_tokens_message} PRACTICUM_TOKEN')
    if TELEGRAM_TOKEN is None:
        tokens_bool = False
        logger.critical(f'{no_tokens_message} TELEGRAM_TOKEN')
    if TELEGRAM_CHAT_ID is None:
        tokens_bool = False
        logger.critical(f'{no_tokens_message} TELEGRAM_CHAT_ID')
    return tokens_bool


def send_message(bot, message):
    '''Отправка сообщения в Телеграм.'''
    try:
        logging.debug(f'Бот отправил сообщение {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Сообщение в Telegram отправлено: {message}')
    except telegram.TelegramError as telegram_error:
        logger.error(
            f'Сообщение в Telegram не отправлено: {telegram_error}')


def get_api_answer(current_timestamp):
    '''Получение данных с API'''
    current_timestamp = current_timestamp or int(time.time())
    params_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': current_timestamp},
    }
    try:
        logging.info(
            'Начало запроса: url = {url},'
            'headers = {headers},'
            'params = {params}'.format(**params_request))
        homework_statuses = requests.get(**params_request)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.InvalidResponseCode(
                'Не удалось получить ответ API, '
                f'ошибка: {homework_statuses.status_code}'
                f'причина: {homework_statuses.reason}'
                f'текст: {homework_statuses.text}')
        return homework_statuses.json()
    except Exception:
        raise exceptions.ConnectionError(
            'Не верный код ответа параметры запроса: url = {url},'
            'headers = {headers},'
            'params = {params}'.format(**params_request))


def check_response(response):
    '''Проверить валидность ответа.'''
    if not isinstance(response, dict):
        message = 'Ошибка в типе ответа API'
        logging.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'Пустой ответ от API'
        logging.error(message)
        raise exceptions.EmptyResponseFromAPI(message)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        message = 'Homeworks не является списком'
        logging.error(message)
        raise TypeError(message)
    return homeworks


def parse_status(homework):
    '''Анализ статуса на изменение'''
    if 'homework_name' not in homework:
        raise KeyError('В ответе отсутствует ключ')
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы - {status}')
    return ('Изменился статус проверки работы "{homework_name}" {verdict}'
            ).format(
        homework_name=homework_name,
        verdict=HOMEWORK_VERDICTS[status])


def main():
    '''Основная логика работы бота.'''
    if not check_tokens():
        logging.critical('Отсутствуют токены!')
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    now = datetime.datetime.now()
    timestamp = int(time.time())
    send_message(
        bot,
        f'Я начал свою работу: {now}'
    )
    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('Домашних работ нет.')
                send_message(bot, 'Изменений нет')
                break
            for homework in homeworks:
                message = parse_status(homework)
                if last_message != message:
                    send_message(bot, message)
                    last_message = message
            timestamp = response.get('current_date')
        except Exception as error:
            if last_message != message:
                message = f'Ошибка в работе бота: {error}'
                send_message(bot, message)
                last_message = message
        else:
            last_message = ''
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
