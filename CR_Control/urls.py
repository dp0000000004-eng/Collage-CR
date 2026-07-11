from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("students/" , views.student_view, name="students"),
    path("student_data/<int:student_id>", views.record_view, name="record"),
    path("create_user/", views.create_user, name="create_user"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout")
]