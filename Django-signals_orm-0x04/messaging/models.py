from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # ✅ track if the message was edited
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver - {'Edited' if self.edited else 'Original'}}: {self.content[:20]}..."
class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="edits")
    
    def __str__(self):
        return f"History of Message {self.message.id} at {self.edited_at} (edited by {self.edited_by}) "
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user} about Message {self.message.id}"
parent_message = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE
    )

def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"

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