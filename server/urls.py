from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🔹 API/App URLs
    path("accounts/", include("accounts.urls")),
    path("content/", include("content.urls")),
    path("gamify/", include("gamify.urls")),
    path("sync/", include("sync.urls")),

    # 🔹 Main Pages
    path("", account_views.login_view, name="login"),
    # path("register/", account_views.choose_role, name="register"),

    # Dashboards
    path("student/dashboard/", account_views.student_dashboard, name="student_dashboard"),
    # path("teacher/dashboard/", account_views.teacher_dashboard, name="teacher_dashboard"),
    # path("parent/dashboard/", account_views.parent_dashboard, name="parent_dashboard"),
]

# 🔹 Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
