from __future__ import absolute_import
from datetime import datetime, timezone
from email.mime.text import MIMEText
import os
import time
import smtplib
import json

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_django.settings")
django.setup()
from django.conf import settings

import requests
from celery import Celery
import backoff
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from api.v1.models import Client, Mailing, Message
from celery_django.logger import mylogger


app = Celery("celery_django")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# создаем задачу celery для ежесуточной отправки статистики
schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="01",
    hour="01",
    day_of_week="*",
    day_of_month="*",
    month_of_year="*",
)
PeriodicTask.objects.get_or_create(
    name="Send_info_to_email",
    task="celery_django.celery.send_info_to_email",
    crontab=schedule,
)


@app.task
def send_info_to_email():
    # задаем настройки
    sender = settings.SEND_EMAIL_FROM
    password = settings.SEND_EMAIL_PASSWORD
    target = settings.SEND_EMAIL_TO
    server = smtplib.SMTP(
        host=settings.SEND_EMAIL_SMTP_HOST, port=settings.SEND_EMAIL_SMTP_PORT
    )
    # формируем тело сообщения
    message = []
    mailings = Mailing.objects.all()
    for mailing in mailings:
        message.append(
            {
                "mailing_id": mailing.id,
                "sent_messages": Message.objects.filter(mailing=mailing)
                .filter(is_sent=True)
                .count(),
                "not_sent_messages": Message.objects.filter(mailing=mailing)
                .filter(is_sent=False)
                .count(),
            }
        )
    message = MIMEText(json.dumps(message), "plain", "utf-8").as_string()
    # отправляем сообщение
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, target, message)
    mylogger.info("Направлена статистика на электронную почту")


@app.task
def send_messages_to_api(stop_time: str, mailing_id: int):
    stop_time = datetime.strptime(stop_time, "%Y-%m-%d %H:%M:%S%z")
    if datetime.now(timezone.utc) >= stop_time:
        return
    # создаем объекты сообщений для данной рассылки
    mailing = Mailing.objects.get(pk=mailing_id)
    clients = Client.objects.filter(mobile_operator=mailing.mobile_operator).filter(
        tag=mailing.tag
    )
    message_objs = (
        Message(is_sent=False, mailing=mailing, client=client) for client in clients
    )
    messages = Message.objects.bulk_create(message_objs)
    # рассылаем сообщения
    session = requests.Session()
    num = 0
    mylogger.info(f"Запуск процесса рассылки id {mailing.id}")
    while num < len(messages):
        if datetime.now(timezone.utc) >= stop_time:
            mylogger.info(f"Истекло конечное время рассылки id {mailing.id}")
            break
        message = messages[num]
        status_code = send(
            message_id=message.id,
            phone=message.client.phone_number,
            text=message.mailing.text,
            session=session,
        )
        # Если последняя отправка не удалась, то делаем паузу на 10 секунд и
        # снова пытаемся отправить последнее сообщение.
        # При успехе, помечаем сообщение как отправленное и переходим к следующему
        if status_code == 200:
            message.is_sent = True
            message.save()
            mylogger.info(
                f"Успешно отправлено сообщение id {message.id} для клиента "
                f"id {message.client.id} по рассылке id {mailing.id}"
            )
        else:
            mylogger.error(
                f"Ошибка отправки сообщения id {message.id} для клиента id "
                f"{message.client.id} по рассылке id {mailing.id}. "
                f"Код ответа внешнего АПИ {status_code}"
            )
            time.sleep(10)
            num -= 1
        num += 1
    mylogger.info(f"Завершение процесса рассылки id {mailing.id}")


def _backoff_message(detail) -> None:
    mylogger.error("Ошибка отправки запроса на внешнее АПИ. Повторная попытка...")


@backoff.on_exception(
    wait_gen=backoff.constant,
    jitter=None,
    interval=1,
    exception=requests.exceptions.ConnectionError,
    on_backoff=_backoff_message,
    max_tries=5,
    raise_on_giveup=False,
    logger=None,
)
def send(message_id: int, phone: str, text: str, session: requests.Session):
    """Попытка отправки сообщения (с пятикратным повторением при неудаче)."""
    url = settings.EXTERNAL_API_URL + str(message_id)
    data = {"id": message_id, "phone": phone, "text": text}
    headers = {"Authorization": f"Bearer {settings.EXTERNAL_API_TOKEN}"}
    response = session.post(url=url, json=data, headers=headers)
    return response.status_code
