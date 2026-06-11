import time
from celery_worker import celery

@celery.task
def long_task(email):
    print(f"sending email to {email}")
    time.sleep(5)
    print("email sent")
    return({"status": "succes", "email":email})
