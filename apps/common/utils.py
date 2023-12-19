from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def generate_otp():
    import secrets

    otp = secrets.token_urlsafe(3)
    return otp


def generate_number_otp(cnt: int):
    import secrets
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    otp = ""
    for i in range(cnt):
        otp += str(secrets.choice(digits))
    return otp


def send_otp_to_email(otp, receivers: list):
    content = render_to_string(
        template_name="common/email/register_confirmation.html",
        context={"otp": otp}
    )
    send_mail(
        subject="OTP for confirmation",
        message="",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=receivers,
        html_message=content,
    )
