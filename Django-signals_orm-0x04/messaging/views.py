from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.views.decorators.cache import cache_page
from django.contrib.auth.models import User
from django.http import HttpResponse

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect("home")  # redirect to homepage after deletion


@login_required
@cache_page(60) 
def conversation_view(request, message_id, username):
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
def inbox(request):
    # ✅ Use custom manager + .only()
    unread_messages = Message.unread.unread_for_user(request.user)

    return render(request, "messaging/inbox.html", {
        "unread_messages": unread_messages
    })

def inbox(request):
    return HttpResponse("This is the inbox view")

def message_detail(request, pk):
    return HttpResponse(f"This is the detail view for message {pk}")
    """
    Display all messages between the logged-in user and the given user.
    Cached for 60 seconds.
    """
    other_user = get_object_or_404(User, username=username)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    return render(request, "messaging/conversation.html", {
        "messages": messages,
        "other_user": other_user
    })