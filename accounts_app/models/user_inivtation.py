import uuid
import secrets

from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .user import User


def get_expiration_datetime():
    return timezone.now() + timezone.timedelta(days=settings.USER_INVITE_EXPIRATION_DAYS)


class UserInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    # Must be a UUID for security reasons. UUID can not be guessed.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=255, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    token = models.CharField(max_length=64, default=secrets.token_urlsafe, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_datetime)

    
    def send_invitation_email(self):
        subject = "You have been invited to join our platform"
        message = f"Click here to join: {settings.SENDING_DOMAIN}/invite/{self.token}"
        from_email = "noreply@yourdomain.com"  # Replace with your valid sender email address
        recipient_list = [self.email]

        send_mail(subject, message, from_email, recipient_list)