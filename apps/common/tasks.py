from celery import shared_task

from . import utils


@shared_task(name="send_mail_task", routing_key="lightweight-tasks")
def send_mail_task(otp, receivers):
    utils.send_otp_to_email(otp=otp, receivers=receivers)
    return "Email sent!"
