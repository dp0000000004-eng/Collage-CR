from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile


def user_can_access_panel(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    try:
        return user.profile.role in (Profile.PROF, Profile.CR)
    except Profile.DoesNotExist:
        return False


def staff_or_teacher_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if user_can_access_panel(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access the admin panel.")
        return redirect("home")

    return wrapper
