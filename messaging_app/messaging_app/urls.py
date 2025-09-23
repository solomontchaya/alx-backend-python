# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),            # chats API endpoints
    path('api-auth/', include('rest_framework.urls')),  # ✅ DRF browsable API login/logout
]
# messaging_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),            # chats API endpoints
    path('api-auth/', include('rest_framework.urls')),  # ✅ DRF browsable API login/logout
]
