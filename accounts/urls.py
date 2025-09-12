from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Role choosing
    path("choose-role/", views.choose_role, name="choose_role"),

    # Registration
    path("register/student/", views.register_student, name="register_student"),
    path("register/teacher/", views.register_teacher, name="register_teacher"),
    path("register/parent/", views.register_parent, name="register_parent"),

    # Login / Logout
    path("login/", views.index, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # 🔹 Forgot + Reset Password Flow
    path("forgot-password/", views.forgot_password, name="forgot_password"),   # ✅ custom (offline link show)
    path("reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"),  # ✅ custom reset
]
