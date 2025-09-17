from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from django.utils import timezone
# Custom User (email-based login)
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    ROLE_CHOICES = (
        ("student", "Student"),
    )

    LANGUAGE_CHOICES = (
        ("english", "English"),
        ("hindi", "Hindi"),
        ("odia", "Odia"),
        ("marathi", "Marathi"),
        ("gujarati", "Gujarati"),
        ("punjabi", "Punjabi"),
        ("telugu", "Telugu"),
        ("bengali", "Bengali"),
        ("kannada", "Kannada"),
        ("urdu", "Urdu"),
        ("other", "Other"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default="english")

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studentprofile")

    student_name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    student_class = models.CharField(
        max_length=10,
        choices=[(str(i), f"Class {i}") for i in range(6, 13)],
        default="6",
    )
    subject = models.CharField(max_length=300, blank=True)  # CSV stored
    board = models.CharField(
        max_length=50,
        choices=[
            ("UP BOARD", "UP BOARD"),
            ("CBSE BOARD", "CBSE BOARD"),
            ("ICSE BOARD", "ICSE BOARD"),
            ("MAHARASHTRA BOARD", "MAHARASHTRA BOARD"),
            ("ODISHA BOARD", "ODISHA BOARD"),
        ],
        default="CBSE BOARD",
    )
    language = models.CharField(max_length=20, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    school_name = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.student_name} ({self.student_class})"




# ================= SUBJECT HIERARCHY =================
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject.name} - {self.title}"


class Topic(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class GameContent(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="games")
    title = models.CharField(max_length=100)
    game_url = models.URLField(help_text="Link to interactive game/simulation")

    def __str__(self):
        return f"{self.topic.title} - {self.title}"
class Note(models.Model):
    """
    Local student notes and drawings.
    drawing: store data URL (base64) of PNG. text: saved text notes.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True, null=True)
    drawing = models.TextField(blank=True, null=True)  # dataURL of PNG
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.email} - {self.title or self.created_at.isoformat()}"

class QuizQuestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct = models.CharField(max_length=1, choices=[("A","A"),("B","B"),("C","C"),("D","D")])

class SmartNote(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    drawing = models.ImageField(upload_to="notes/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

# accounts/models.py (append at end)
from django.conf import settings
from django.utils import timezone

class StudentProgress(models.Model):
    """
    Track lessons/quizzes completed by a student.
    We store one row per (user, subject, lesson) completion.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_entries")
    subject = models.ForeignKey('accounts.Subject', on_delete=models.CASCADE)
    lesson = models.ForeignKey('accounts.Lesson', on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey('accounts.Topic', on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "subject", "lesson", "topic")

    def mark_completed(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subject_id": self.subject_id,
            "lesson_id": self.lesson_id,
            "topic_id": self.topic_id,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
