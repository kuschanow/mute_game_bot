from celery import shared_task

from bot.utils import collect_garbage


@shared_task
def garbage_collector_task():
    collect_garbage()
