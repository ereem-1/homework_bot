class NotForSending(Exception):
    """Не для пересылки в телеграм."""

    pass


class InvalidResponseCode(Exception):
    """Не верный код ответа."""

    pass


class ConnectionError(Exception):
    """Не верный код ответа."""

    pass


class EmptyResponseFromAPI(Exception):
    """Пустой ответ от API."""

    pass


class TelegramError(Exception):
    """Ошибка телеграма."""

    pass
