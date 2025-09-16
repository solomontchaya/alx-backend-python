from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message, ConversationParticipant
from .serializers import (
    UserSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    ConversationListSerializer,
    MessageSerializer,
    CreateMessageSerializer,
    AddParticipantSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling conversations
    """
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return ConversationSerializer
        elif self.action == 'messages':
            return MessageSerializer
        elif self.action == 'add_participants':
            return AddParticipantSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """
        Return conversations where the authenticated user is a participant
        """
        user = self.request.user
        return Conversation.objects.filter(
            conversation_participants__user=user
        ).prefetch_related(
            Prefetch('conversation_participants__user', queryset=User.objects.all()),
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-sent_at')[:10])
        ).distinct().order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Create conversation and ensure the creator is added as participant
        """
        participant_ids = serializer.validated_data.get('participant_ids', [])
        
        # Add the current user to participants if not already included
        if self.request.user.user_id not in participant_ids:
            participant_ids.append(self.request.user.user_id)
        
        conversation = serializer.save()
        
        # Return the created conversation with full details
        return conversation
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = self.perform_create(serializer)
        
        # Return detailed response
        detail_serializer = ConversationDetailSerializer(
            conversation, 
            context=self.get_serializer_context()
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get conversation details with messages
        """
        instance = self.get_object()
        
        # Check if user is a participant
        if not instance.conversation_participants.filter(user=request.user).exists():
            return Response(
                {"detail": "Not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ConversationDetailSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        """
        Get all messages for a specific conversation
        """
        conversation = self.get_object()
        
        # Check if user is a participant
        if not conversation.conversation_participants.filter(user=request.user).exists():
            return Response(
                {"detail": "Not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        messages = conversation.messages.select_related('sender').order_by('sent_at')
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        """
        Send a message to an existing conversation
        """
        conversation = self.get_object()
        
        # Check if user is a participant
        if not conversation.conversation_participants.filter(user=request.user).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateMessageSerializer(
            data=request.data,
            context={'request': request, 'conversation': conversation}
        )
        
        if serializer.is_valid():
            # Ensure the message is associated with this conversation
            message = serializer.save(conversation=conversation)
            
            # Return the created message
            message_serializer = MessageSerializer(message, context=self.get_serializer_context())
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='add-participants')
    def add_participants(self, request, pk=None):
        """
        Add participants to an existing conversation
        """
        conversation = self.get_object()
        
        # Check if user is a participant (only participants can add others)
        if not conversation.conversation_participants.filter(user=request.user).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AddParticipantSerializer(data=request.data)
        
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            
            # Add new participants
            added_count = 0
            for user_id in user_ids:
                try:
                    user = User.objects.get(user_id=user_id)
                    # Check if user is already a participant
                    if not conversation.conversation_participants.filter(user=user).exists():
                        ConversationParticipant.objects.create(
                            conversation=conversation,
                            user=user
                        )
                        added_count += 1
                except User.DoesNotExist:
                    continue
            
            return Response(
                {"detail": f"Added {added_count} participants to the conversation."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling messages across all conversations
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return messages from conversations where the user is a participant
        """
        user = self.request.user
        return Message.objects.filter(
            conversation__conversation_participants__user=user
        ).select_related('sender', 'conversation').order_by('-sent_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new message (alternative to conversation send-message endpoint)
        """
        serializer = CreateMessageSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            conversation_id = serializer.validated_data['conversation'].conversation_id
            
            # Check if user is a participant in the conversation
            if not ConversationParticipant.objects.filter(
                conversation_id=conversation_id, 
                user=request.user
            ).exists():
                return Response(
                    {"detail": "You are not a participant in this conversation."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            message = serializer.save(sender=request.user)
            message_serializer = MessageSerializer(message, context=self.get_serializer_context())
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List all messages across user's conversations with optional filtering
        """
        queryset = self.get_queryset()
        
        # Optional filters
        conversation_id = request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)