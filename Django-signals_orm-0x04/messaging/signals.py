from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification
from .models import Message, MessageHistory
from django.contrib.auth.models import User

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
    if instance.pk:  # Means the message already exists (update)
        old_message = Message.objects.get(pk=instance.pk)
        if old_message.content != instance.content:
            MessageHistory.objects.create(
                message=old_message,
                old_content=old_message.content,
                edited_by=instance.sender  # assuming the sender edits their own message
            )
            instance.edited = True

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    # Delete all messages where user was sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications
    Notification.objects.filter(user=instance).delete()

    # Delete message histories related to user's messages
    MessageHistory.objects.filter(edited_by=instance).delete()