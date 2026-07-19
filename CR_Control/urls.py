from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("students/" , views.student_view, name="students"),
    path("student_data/<int:student_id>", views.record_view, name="record"),
    path("create_user/", views.create_user, name="create_user"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # path("delete/<int:prof_id>/", views.delete, name="delete"),

    path("panel/", admin_views.panel_dashboard, name="panel_dashboard"),
    path("panel/attendance/", admin_views.panel_mark_attendance, name="panel_attendance"),
    path("panel/students/", admin_views.panel_students, name="panel_students"),
    path("panel/students/<int:student_id>/edit/", admin_views.panel_student_edit, name="panel_student_edit"),
    path("panel/students/<int:student_id>/delete/", admin_views.panel_student_delete, name="panel_student_delete"),
    path("panel/branches/", admin_views.panel_branches, name="panel_branches"),
    path("panel/branches/<int:branch_id>/delete/", admin_views.panel_branch_delete, name="panel_branch_delete"),
    path("panel/subjects/", admin_views.panel_subjects, name="panel_subjects"),
    path("panel/subjects/<int:subject_id>/delete/", admin_views.panel_subject_delete, name="panel_subject_delete"),
    path("panel/sessions/", admin_views.panel_sessions, name="panel_sessions"),
    path("panel/sessions/<int:session_id>/delete/", admin_views.panel_session_delete, name="panel_session_delete"),
]