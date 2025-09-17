# ------------------ STUDENT REGISTRATION ------------------
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_student(request):
    from .forms import StudentRegisterForm
    if request.method == "POST":
        form = StudentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect("accounts:login")
    else:
        form = StudentRegisterForm()
    return render(request, "register_student.html", {"form": form})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import activate
from .forms import (
    StudentRegisterForm,
    LoginForm, ForgotPasswordForm
)
from .models import StudentProfile, Subject
from .forms import StudentRegisterForm





import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone

# ------------------ REGISTER ------------------




# ------------------ LOGIN / LOGOUT ------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user:
                try:
                    student = StudentProfile.objects.get(user=user)
                except StudentProfile.DoesNotExist:
                    messages.error(request, "Student profile not found.")
                    return redirect("accounts:login")

                login(request, user)
                return redirect("accounts:student_dashboard")
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# ------------------ DASHBOARDS ------------------
@login_required
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("accounts:login")

    # Language handling
    lang = (student.language or "english").lower()
    language_map = {
        "english": "en",
        "hindi": "hi",
        "marathi": "mr",
        "bengali": "bn",
        "tamil": "ta",
        "gujarati": "gu",
        "kannada": "kn",
        "punjabi": "pa",
        "telugu": "te",
        "urdu": "ur",
        "odia": "or",
    }
    lang_code = language_map.get(lang, "en")
    activate(lang_code)
    request.session["django_language"] = lang_code

    # Show only subjects selected by student
    selected_subjects = [s.strip() for s in (student.subject or "").split(",") if s.strip()]
    subject_map = {
        "math": "Math",
        "hindi": "Hindi",
        "english": "English",
        "computer science": "Computer Science",
        "physics": "Physics",
        "chemistry": "Chemistry",
        "biology": "Biology",
        "geography": "Geography",
        "history": "History",
        "ethics": "Ethics",
    }
    subject_cards = [subject_map.get(subj, subj.title()) for subj in selected_subjects]

    return render(request, "student_dashboard.html", {"student": student, "subject_cards": subject_cards})




# ------------------ FORGOT PASSWORD ------------------
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            messages.success(request, f"Password reset link sent to {email}.")
            return redirect("accounts:login")
    else:
        form = ForgotPasswordForm()
    return render(request, "forgot_password.html", {"form": form})


# ------------------ CHANGE LANGUAGE ------------------
from django.utils import translation

def change_language(request):
    current_lang = translation.get_language()
    new_lang = "hi" if current_lang == "en" else "en"
    translation.activate(new_lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = new_lang
    return redirect(request.META.get("HTTP_REFERER", "/"))


def edit_profile(request):
    student = request.user.studentprofile
    if request.method == "POST":
        form = StudentRegisterForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("accounts:student_dashboard")
    else:
        form = StudentRegisterForm(instance=student)
    return render(request, "edit_profile.html", {"form": form})


# accounts/views.py (append)

@login_required
@require_http_methods(["GET"])
def api_get_quiz(request, quiz_id):
    """
    Return quiz data (questions + choices) for quiz_id.
    Only authenticated students can access.
    """
    from content.models import Quiz, Question, Choice
    user = request.user

    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return JsonResponse({"error": "Quiz not found"}, status=404)

    # Build JSON payload
    questions = []
    for q in quiz.questions.all():
        choices = []
        for c in q.choices.all():
            choices.append({"id": c.id, "text": c.text})
        questions.append({
            "id": q.id,
            "text": q.text,
            "marks": q.marks,
            "qtype": q.qtype,
            "choices": choices
        })

    data = {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "time_limit": quiz.time_limit or 0,
        "total_marks": quiz.total_marks or sum([q.marks for q in quiz.questions.all()]),
        "questions": questions
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def api_submit_quiz(request, quiz_id):
    """
    Accepts JSON: { answers: [{question_id: id, choice_id: id}, ...], subject_id, lesson_id, topic_id }
    Grades the quiz, stores StudentProgress (marks lesson completed on pass or always mark).
    Returns: {score, total, details: [{question,text,selected,correct,correct_answer}] , progress_percent}
    """
    from content.models import Quiz, Question, Choice, Lesson, Subject, Topic
    from .models import StudentProgress

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    answers = payload.get("answers", [])
    subject_id = payload.get("subject_id")
    lesson_id = payload.get("lesson_id")
    topic_id = payload.get("topic_id")

    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return JsonResponse({"error": "Quiz not found"}, status=404)

    total_marks = 0
    score = 0
    details = []

    # Build map of correct choice id per question
    correct_map = {}
    for q in quiz.questions.all():
        total_marks += (q.marks or 1)
        # find correct choice(s) (support multiple correct as safety)
        correct_choices = list(q.choices.filter(is_correct=True).values_list('id', flat=True))
        correct_map[q.id] = set(correct_choices)

    # evaluate answers list
    for ans in answers:
        qid = int(ans.get("question_id"))
        chosen = ans.get("choice_id")
        qobj = None
        try:
            qobj = quiz.questions.get(pk=qid)
        except Question.DoesNotExist:
            continue
        q_marks = qobj.marks or 1
        total_for_q = q_marks
        chosen_id = None
        if chosen is not None:
            try:
                chosen_id = int(chosen)
            except:
                chosen_id = None

        is_correct = False
        if chosen_id and chosen_id in correct_map.get(qid, set()):
            is_correct = True
            score += q_marks

        # Find correct answer text for response:
        correct_choice_obj = qobj.choices.filter(is_correct=True).first()
        correct_text = correct_choice_obj.text if correct_choice_obj else None

        chosen_text = None
        if chosen_id:
            cobj = qobj.choices.filter(pk=chosen_id).first()
            chosen_text = cobj.text if cobj else None

        details.append({
            "question_id": qid,
            "question": qobj.text,
            "selected_choice_id": chosen_id,
            "selected_text": chosen_text,
            "correct": is_correct,
            "correct_answer": correct_text,
            "marks": q_marks
        })

    # Persist progress: mark lesson+topic completed for student (create or update)
    if subject_id:
        try:
            subject = Subject.objects.get(pk=subject_id)
        except Subject.DoesNotExist:
            subject = None
    else:
        subject = None
    lesson = None
    topic = None
    if lesson_id:
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
        except:
            lesson = None
    if topic_id:
        try:
            topic = Topic.objects.get(pk=topic_id)
        except:
            topic = None

    # create or mark StudentProgress
    if subject:
        sp, created = StudentProgress.objects.get_or_create(
            user=request.user,
            subject=subject,
            lesson=lesson,
            topic=topic,
            defaults={"completed": True, "completed_at": timezone.now()}
        )
        if not sp.completed:
            sp.completed = True
            sp.completed_at = timezone.now()
            sp.save()

    # Compute subject progress percent: (#completed lessons for this user & subject) / (total lessons in subject)
    progress_percent = 0
    if subject:
        # total unique lessons in subject
        total_lessons = subject.lessons.count()
        if total_lessons > 0:
            # count distinct completed lesson ids for this user & subject
            completed_lessons = StudentProgress.objects.filter(user=request.user, subject=subject, completed=True).exclude(lesson__isnull=True).values('lesson').distinct().count()
            progress_percent = int((completed_lessons / total_lessons) * 100)

    # Optional: store last quiz result (you can extend model to store quiz results)
    result = {
        "score": score,
        "total": total_marks,
        "details": details,
        "progress_percent": progress_percent
    }
    return JsonResponse(result)


@login_required
@require_http_methods(["GET"])
def api_subject_progress(request, subject_id):
    """
    Return student's progress percent for a subject.
    """
    from .models import StudentProgress
    from content.models import Subject
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({"error": "Subject not found"}, status=404)

    total_lessons = subject.lessons.count()
    completed_lessons = StudentProgress.objects.filter(user=request.user, subject=subject, completed=True).exclude(lesson__isnull=True).values('lesson').distinct().count()
    percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    return JsonResponse({"subject_id": subject.id, "percent": percent})
