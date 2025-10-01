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
class ThreadedConversationTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass")
        self.bob = User.objects.create_user(username="bob", password="pass")

        self.msg1 = Message.objects.create(sender=self.alice, receiver=self.bob, content="Hello Bob!")
        self.msg2 = Message.objects.create(sender=self.bob, receiver=self.alice, content="Hi Alice!", parent_message=self.msg1)
        self.msg3 = Message.objects.create(sender=self.alice, receiver=self.bob, content="How are you?", parent_message=self.msg2)

    def test_thread_structure(self):
        thread = self.msg1.get_thread()
        self.assertEqual(len(thread), 1)
        self.assertEqual(thread[0]["content"], "Hi Alice!")
        self.assertEqual(len(thread[0]["replies"]), 1)
        self.assertEqual(thread[0]["replies"][0]["content"], "How are you?")