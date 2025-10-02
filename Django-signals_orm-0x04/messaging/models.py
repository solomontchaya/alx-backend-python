from django.db import models
from django.contrib.auth.models import User


class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Returns only unread messages for the given user (as receiver).
        Optimized with `.only()` to fetch just required fields.
        """
        return (
            super()
            .get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "content", "timestamp")
        )


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # track if edited
    read = models.BooleanField(default=False)    # track if read

    # Threaded replies
    parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

    # Managers
    objects = models.Manager()       # Default
    unread = UnreadMessagesManager() # Custom

    def __str__(self):
        edited_flag = " (Edited)" if self.edited else ""
        return f"{self.sender.username} → {self.receiver.username}{edited_flag}: {self.content[:20]}"

    def get_thread(self):
        """
        Recursive function to fetch all replies (nested).
        """
        thread = []
        for reply in self.replies.all().select_related("sender", "receiver"):
            thread.append({
                "id": reply.id,
                "content": reply.content,
                "sender": reply.sender.username,
                "timestamp": reply.timestamp,
                "replies": reply.get_thread()  # recursion
            })
        return thread


class MessageHistory(models.Model):
    message = models.ForeignKey("messaging.Message", on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="edits")

    def __str__(self):
        return f"History of Message {self.message.id} at {self.edited_at} (edited by {self.edited_by})"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey("messaging.Message", on_delete=models.CASCADE, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} about Message {self.message.id}"
