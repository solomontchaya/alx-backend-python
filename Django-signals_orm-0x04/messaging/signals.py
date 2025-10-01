from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    When a new message is created, automatically notify the receiver.
    """
    if created:  # Only on new messages, not updates
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
