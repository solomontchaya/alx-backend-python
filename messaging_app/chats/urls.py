from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]

# Alternatively, if you want more control over URLs:
"""
urlpatterns = [
    path('api/conversations/', ConversationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='conversation-list'),
    
    path('api/conversations/<uuid:pk>/', ConversationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='conversation-detail'),
    
    path('api/conversations/<uuid:pk>/messages/', ConversationViewSet.as_view({
        'get': 'messages'
    }), name='conversation-messages'),
    
    path('api/conversations/<uuid:pk>/send-message/', ConversationViewSet.as_view({
        'post': 'send_message'
    }), name='conversation-send-message'),
    
    path('api/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='message-list'),
]
"""