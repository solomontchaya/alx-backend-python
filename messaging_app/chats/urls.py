from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers
from chats.views import ConversationViewSet, MessageViewSet  # adjust if needed

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(conversations_router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
