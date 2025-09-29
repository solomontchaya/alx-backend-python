class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        """
        Return unread messages for a specific user.
        Optimized with .only() to fetch necessary fields.
        """
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only("id", "sender", "receiver", "content", "timestamp")
        )