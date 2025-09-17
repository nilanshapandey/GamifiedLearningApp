from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/student/", views.register_student, name="register_student"),
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path('change-language/', views.change_language, name='change_language'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path('api/quiz/<int:quiz_id>/', views.api_get_quiz, name='api_get_quiz'),
    path('api/quiz/<int:quiz_id>/submit/', views.api_submit_quiz, name='api_submit_quiz'),
    path('api/subject/<int:subject_id>/progress/', views.api_subject_progress, name='api_subject_progress'),
]
