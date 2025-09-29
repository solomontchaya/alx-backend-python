from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from messaging.models import Message

@login_required
def inbox(request):
    """
    Display unread messages for the logged-in user.
    """
    unread_messages = Message.unread.for_user(request.user)
    return render(request, "messaging/inbox.html", {"unread_messages": unread_messages})

@login_required
@cache_page(60)  # cache for 60 seconds
def conversation_view(request, username):
    """
    Display conversation between the logged-in user and another user.
    Cached for 60 seconds.
    """
    other_user = get_object_or_404(User, username=username)

    messages = (
        Message.objects.filter(
            sender__in=[request.user, other_user],
            receiver__in=[request.user, other_user]
        )
        .select_related("sender", "receiver")
        .order_by("timestamp")
    )

    return render(request, "chats/conversation.html", {
        "other_user": other_user,
        "messages": messages,
    })

@login_required
def delete_user(request):
    """
    Allow a logged-in user to delete their own account.
    """
    user = request.user
    user.delete()   # This triggers post_delete signal
    logout(request)  # Log them out after deletion
    return redirect('/')  # Redirect to homepage (or goodbye page)
