from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification
from .models import Message, MessageHistory

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
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before saving a Message, check if it's being updated.
    If yes, log the old content into MessageHistory.
    """
    if instance.pk:  # Only if message already exists (update, not create)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Save old content to history
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content
                )
                instance.edited = True  # Mark as edited
        except Message.DoesNotExist:
            pass
