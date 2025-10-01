from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

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
