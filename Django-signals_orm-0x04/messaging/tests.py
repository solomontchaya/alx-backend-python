from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification

class MessagingSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="pass123")
        self.receiver = User.objects.create_user(username="bob", password="pass123")

    def test_message_creates_notification(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        # A notification should be created automatically
        notification = Notification.objects.filter(user=self.receiver, message=message).first()
        self.assertIsNotNone(notification)
        self.assertFalse(notification.is_read)

class MessageEditSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="pass123")
        self.receiver = User.objects.create_user(username="bob", password="pass123")
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

    def test_edit_creates_history(self):
        # Edit the message
        self.message.content = "Hello Bob! How are you?"
        self.message.save()

        history = MessageHistory.objects.filter(message=self.message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Hello Bob!")
        self.assertTrue(self.message.edited)

class UserDeletionSignalTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass123")
        self.bob = User.objects.create_user(username="bob", password="pass123")

        self.message = Message.objects.create(sender=self.alice, receiver=self.bob, content="Hi Bob!")
        Notification.objects.create(user=self.bob, message=self.message)

        # Simulate an edit to create a MessageHistory
        self.message.content = "Hi Bob! (edited)"
        self.message.save()

    def test_user_deletion_cleans_data(self):
        self.alice.delete()

        # Messages, notifications, histories tied to Alice should be gone
        self.assertFalse(Message.objects.filter(sender=self.alice).exists())
        self.assertFalse(Notification.objects.filter(user=self.alice).exists())
        self.assertFalse(MessageHistory.objects.filter(message__sender=self.alice).exists())

class UnreadMessagesManagerTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass123")
        self.bob = User.objects.create_user(username="bob", password="pass123")

        Message.objects.create(sender=self.alice, receiver=self.bob, content="Hi Bob!", read=False)
        Message.objects.create(sender=self.alice, receiver=self.bob, content="Another one", read=True)

    def test_unread_messages_for_user(self):
        unread = Message.unread.for_user(self.bob)
        self.assertEqual(unread.count(), 1)
        self.assertEqual(unread.first().content, "Hi Bob!")