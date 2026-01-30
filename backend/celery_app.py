from __future__ import absolute_import
import os
import platform
from celery import Celery
from celery.schedules import crontab
from config import Config
from flask import Flask

def create_minimal_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from extensions import db, mail
    db.init_app(app)
    mail.init_app(app)
    
    return app

flask_app = create_minimal_app()

celery = Celery(
    'parking_app',
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
    include=['tasks']
)

celery.conf.update(
    result_expires=3600,  
    timezone='Asia/Kolkata',
    enable_utc=False,
    worker_max_tasks_per_child=1000,
)


if platform.system() == 'Windows':
    celery.conf.update(
        broker_connection_retry_on_startup=True,
        worker_pool='solo',  
        broker_connection_max_retries=10,
    )

celery.conf.beat_schedule = {
    'monthly-user-report': {
        'task': 'tasks.send_monthly_reports',
        'schedule': crontab(minute='0', hour='0', day_of_month='1'),
        # 'schedule': crontab(minute='*', hour='*'), 
    },
    'send-evening-reminders': {
        'task': 'tasks.send_evening_reminders',
        'schedule': crontab(hour='20', minute='0'),
        # 'schedule': crontab(minute='*', hour='*'), 
    },
}

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

def init_celery(app):
    return celery