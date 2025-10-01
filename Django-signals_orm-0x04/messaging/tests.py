from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class MessagingSignalTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="1234")
        self.receiver = User.objects.create_user(username="bob", password="1234")

    def test_notification_created_on_new_message(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        notification = Notification.objects.get(user=self.receiver, message=message)

        self.assertFalse(notification.is_read)
        self.assertEqual(notification.user.username, "bob")
class UserDeleteTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="testpass")
        self.user2 = User.objects.create_user(username="bob", password="testpass")
        self.message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hi Bob!")
        Notification.objects.create(user=self.user2, message=self.message)
        MessageHistory.objects.create(message=self.message, old_content="Old Hi", edited_by=self.user1)

    def test_user_delete_cleans_data(self):
        self.user1.delete()

        self.assertFalse(Message.objects.filter(sender=self.user1).exists())
        self.assertFalse(MessageHistory.objects.filter(edited_by=self.user1).exists())
        self.assertFalse(Notification.objects.filter(user=self.user1).exists())
