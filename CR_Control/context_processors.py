from .decorators import user_can_access_panel


def panel_access(request):
    return {"can_access_panel": user_can_access_panel(request.user)}
