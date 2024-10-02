import os
import requests


def get_server_response(session_id: str, message: str) -> list:
    """
    Получение информации с удаленного сервера

    :param session_id: уникальный идентификатор сессии
    :param message: тело сообщения на удаленный сервер
    :return: массив сообщений от сервера
    """
    exception_body = [
        {
            'text': 'Проблема при запросе на сервер, пожалуйста, очистите историю поиска'
        }
    ]
    rasa_host, rasa_port = os.getenv("RASA_HOST"), os.getenv("RASA_PORT")
    try:
        res = requests.post(
            f"{rasa_host}:{rasa_port}/webhooks/rest/webhook",
            json={"sender": session_id, "message": message}
        )
        if not res.json():
            return exception_body

        return res.json()

    except requests.exceptions.ConnectionError:
        return exception_body
