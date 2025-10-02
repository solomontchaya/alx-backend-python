from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),  # example: show inbox
    path("<int:pk>/", views.message_detail, name="message_detail"),  # view single message
]
