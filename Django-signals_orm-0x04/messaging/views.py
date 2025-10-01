from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect("home")  # redirect to homepage after deletion
