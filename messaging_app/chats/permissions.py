from rest_framework.permissions import BasePermission, IsAuthenticated

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission:
    - User must be authenticated
    - User must be a participant in the conversation
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj will be a Conversation or a Message instance.
        We assume:
          - Conversation has participants (ManyToMany with User)
          - Message has a conversation field (FK) and belongs to one Conversation
        """
        if hasattr(obj, "participants"):  # conversation object
            return request.user in obj.participants.all()
        if hasattr(obj, "conversation"):  # message object
            return request.user in obj.conversation.participants.all()
        return False
