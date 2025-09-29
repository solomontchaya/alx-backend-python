from django.db import models
from django.contrib.auth.models import User
from messaging.managers import UnreadMessagesManager
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(   # NEW FIELD
        User,
        null=True,
        blank=True,
        related_name='edited_messages',
        on_delete=models.SET_NULL
    )

    # Self-referential FK for replies
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    read = models.BooleanField(default=False)

    objects = models.Manager()  # default manager
    unread = UnreadMessagesManager()  # custom manager

    def __str__(self):
        return f"Msg {self.id} from {self.sender} to {self.receiver}"

    @property
    def is_reply(self):
        return self.parent_message is not None

    def get_thread(self):
        """
        Recursive method to fetch all replies in a threaded conversation.
        """
        replies = []
        for reply in self.replies.all().select_related("sender", "receiver").prefetch_related("replies"):
            replies.append({
                "id": reply.id,
                "sender": reply.sender.username,
                "content": reply.content,
                "timestamp": reply.timestamp,
                "replies": reply.get_thread()  # recursion
            })
        return replies

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} about message {self.message.id}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name="history", on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of message {self.message.id} at {self.edited_at}"