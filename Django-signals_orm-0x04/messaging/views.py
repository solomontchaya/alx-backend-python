from django.shortcuts import render, get_object_or_404
from .models import Message
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect("home")  # redirect to homepage after deletion
def conversation_view(request, message_id):
    root_message = get_object_or_404(
        Message.objects.select_related("sender", "receiver").prefetch_related("replies__sender", "replies__receiver" .first()
),
)

    if not root_message:
        return render(request, "messaging/not_found.html", status=404)  
   
    conversation = {
        "id": root_message.id,
        "content": root_message.content,
        "sender": root_message.sender.username,
        "timestamp": root_message.timestamp,
        "replies": root_message.get_thread()
    }
    return render(request, "messaging/conversation.html", {"conversation": conversation})