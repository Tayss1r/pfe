from celery import Celery
from .mail import create_message, mail
from typing import List
from asgiref.sync import async_to_sync

celery_app =Celery()

celery_app.config_from_object('app.core.config')

@celery_app.task(name='app.celery_tasks.send_email')
def send_email(recipients: List[str], subject: str, body: str):
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body
    )
    async_to_sync(mail.send_message)(message) 