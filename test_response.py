import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from telegram import Bot
from dotenv import load_dotenv

bot = Bot(token='6924098150:AAG0taPeYO2W_zlqeGnOzoiQrnX2i2eNzNI')
PRACTICUM_TOKEN = 'y0_AgAAAAAE5v4MAAYckQAAAADwOHoX_pEBtTLeThiOM0Vi5o_0_LkrdkY'
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
chat_id = 5504324457

'''# Делаем GET-запрос к эндпоинту:
response = requests.get(URL).json()

# Рассмотрим структуру и содержимое переменной response
print(response)

# Посмотрим, какого типа переменная response
print(type(response))

# response - это список. А какой длины?
print(len(response))

# Посмотрим, какого типа первый элемент
print(type(response[0]))'''


def get_api_answer(current_timestamp):
    """Выполняет запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={"from_date": timestamp}
    )
    homework_statuses = requests.get(**params)
    print(homework_statuses)
    print('asd')
