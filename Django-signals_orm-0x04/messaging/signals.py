from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    When a new Message is created, generate a Notification for the receiver.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Before saving a Message, check if content has changed.
    If yes, log the old content in MessageHistory and set edited=True.
    """
    if not instance.pk:
        # New message → nothing to compare
        return

    try:
        old_instance = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old_instance.content != instance.content:
        # Save old content to history
        MessageHistory.objects.create(
            message=instance,
            old_content=old_instance.content
        )
        # Mark as edited
        instance.edited = True

@receiver(post_delete, sender=User)
def delete_related_data(sender, instance, **kwargs):
    """
    When a User is deleted, clean up all related messages,
    notifications, and message histories.
    """
    # Delete messages where the user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications for this user
    Notification.objects.filter(user=instance).delete()

    # Delete message histories tied to messages sent/received by this user
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()