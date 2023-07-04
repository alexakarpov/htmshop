from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    msg = "You have securely logged out. Thank you for visiting."
    messages.add_message(request, messages.INFO, msg)
