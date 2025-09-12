from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import StudentRegisterForm, TeacherRegisterForm, ParentRegisterForm, LoginForm
from .models import Profile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

User = get_user_model()


# -------------------------
# Role Choose Page
# -------------------------
def choose_role(request):
    return render(request, "choose_role.html")


# -------------------------
# Common Register Handler
# -------------------------
def handle_register(request, form_class, role):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"{role.capitalize()} registered successfully! Please login.")
            return redirect("login")
    else:
        form = form_class()
    return render(request, "register.html", {"form": form, "role": role})


def register_student(request):
    return handle_register(request, StudentRegisterForm, "student")


def register_teacher(request):
    return handle_register(request, TeacherRegisterForm, "teacher")


def register_parent(request):
    return handle_register(request, ParentRegisterForm, "parent")


# -------------------------
# Login (index.html)
# -------------------------
def index(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]

            user = authenticate(request, username=email, password=password)
            if user:
                try:
                    profile = Profile.objects.get(user=user, role=role)
                    login(request, user)
                    request.session["lang"] = profile.language

                    if role == "student":
                        return redirect("student_dashboard")
                    elif role == "teacher":
                        return redirect("teacher_dashboard")
                    elif role == "parent":
                        return redirect("parent_dashboard")
                except Profile.DoesNotExist:
                    messages.error(request, "Profile for this role does not exist.")
            else:
                messages.error(request, "Invalid credentials!")
    else:
        form = LoginForm()

    return render(request, "index.html", {"form": form})


# -------------------------
# Dashboards
# -------------------------
def student_dashboard(request):
    return render(request, "student_dashboard.html", {"lang": request.session.get("lang", "en")})


def teacher_dashboard(request):
    return render(request, "teacher_dashboard.html", {"lang": request.session.get("lang", "en")})


def parent_dashboard(request):
    return render(request, "parent_dashboard.html", {"lang": request.session.get("lang", "en")})


# -------------------------
# Logout
# -------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# -------------------------
# Forgot Password
# -------------------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://127.0.0.1:8000/accounts/reset-password/{uid}/{token}/"

            messages.success(request, f"Password reset link (offline mode): {reset_link}")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Email not found!")

    return render(request, "accounts/forgot_password.html")


# -------------------------
# Reset Password
# -------------------------
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password reset successful! Please login.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match!")

        return render(request, "accounts/reset_password.html")
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")
