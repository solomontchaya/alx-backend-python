from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
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