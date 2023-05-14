import sys
import time
import os
import logging
import requests
from dotenv import load_dotenv
import telegram

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("homework.log", encoding='UTF-8')
    ],
    format="%(asctime)s, %(name)s, %(levelname)s, %(message)s"
)


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {"from_date": 1678458842}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка валидности токенов и ID пользователя."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправляем сообщение пользователю."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug("Сообщение отправлено.")
    except Exception:
        logging.error("Сообщение не отправлено.")


def get_api_answer(timestamp):
    """Запрос к API yandex practicum."""
    payload = {"from_date": timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except requests.RequestException as error:
        logging.error(f"Ошибка службы API {error}")
        raise TypeError(f"Ошибка службы API {error}")
    if response.status_code != 200:
        logging.error(f"Ошибка {response.status_code}")
        raise ValueError(f"Ошибка {response.status_code}")
    return response.json()


def check_response(response):
    """Проверка ответа API."""
    if type(response) == dict:
        try:
            if type(response.get("homeworks")) == list:
                logging.info("Список проверен и передан.")
                return response.get("homeworks")[0]
        except IndexError:
            logging.error("Отсувстует информация о домашней работе.")
            raise IndexError("Отсувстует информация о домашней работе.")
        else:
            logging.error("Не верный формат данных.")
            raise TypeError("Не верный формат данных.")
    else:
        logging.error("Не верный формат данных.")
        raise TypeError("Не верный формат данных.")


def parse_status(homeworks):
    """Извлекаем статус домашней работы."""
    if "homework_name" not in homeworks:
        logging.error("Отсувстует информация о домашней работе.")
        raise Exception("Ваша работа еще не взята на проверку.")
    else:
        homework_name = homeworks["homework_name"]
        for key, value in HOMEWORK_VERDICTS.items():
            if key not in HOMEWORK_VERDICTS.keys():
                logging.error("Отсувствует статус работы.")
                raise Exception("Отсувствует статус работы.")
            elif key == homeworks["status"]:
                verdict = value
        logging.debug("Успешно извлечен статус домашней работы.")
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    cache_message = ""
    cache_message_error = ""

    while True:
        if not check_tokens():
            logging.critical("Отсувствует переменная окружения")
            sys.exit()
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks)
                if cache_message != message:
                    send_message(bot, message)
                    cache_message = message
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message_error = f"Сбой работы в программе. {error}"
            logging.error(f"Сбой работы в программе. {error}")
            if cache_message_error != message_error:
                send_message(bot, message_error)
                cache_message_error = message_error
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
