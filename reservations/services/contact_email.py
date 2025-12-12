
# reservations/services/contact_email.py
from django.core.mail import send_mail
from django.conf import settings

def send_contact_email(name, email, subject, message):
    support_email = getattr(settings, "COMPANY_SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL)
    body = (
        f"New contact submission\n\n"
        f"From: {name} <{email}>\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n"
    )
    send_mail(
        subject=f"[Contact] {subject}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL or support_email,
        recipient_list=[support_email],
        fail_silently=False,
    )
