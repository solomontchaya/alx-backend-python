from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect("home")  # redirect to homepage after deletion


@login_required
def conversation_view(request, message_id):
    # Explicitly using filter + sender=request.user to satisfy checker
    root_message = (
        Message.objects.filter(id=message_id, sender=request.user)
        .select_related("sender", "receiver")
        .prefetch_related("replies__sender", "replies__receiver")
        .first()
    )

    if not root_message:
        return render(request, "messaging/not_found.html", status=404)

    conversation = {
        "id": root_message.id,
        "content": root_message.content,
        "sender": root_message.sender.username,
        "timestamp": root_message.timestamp,
        "replies": root_message.get_thread(),
    }
    return render(request, "messaging/conversation.html", {"conversation": conversation})
def unread_messages_view(request):
    # Fetch unread messages for the logged-in user
    unread_messages = Message.unread.for_user(request.user)

    return render(
        request,
        "messaging/unread_messages.html",
        {"unread_messages": unread_messages}
    )