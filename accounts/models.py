from django.contrib.auth.models import AbstractUser
from django.db import models


# 🔹 Custom User (email-based login)
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# 🔹 Profile model (Student/Teacher/Parent ke liye)
class Profile(models.Model):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
    )

    LANGUAGE_CHOICES = (
        ("english", "English"),
        ("hindi", "Hindi"),
        ('odia', 'Odia'),
        ('malayalam', 'Malayalam'),
        ('tamil', 'Tamil'),
        ('gujarati', 'Gujarati'),
        ('marathi', 'Marathi'),
        ('telugu', 'Telugu'),
        ('bengali', 'Bengali'),
        ('punjabi', 'Punjabi'),
        ('kannada', 'Kannada'),
        ('urdu', 'Urdu'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    unique_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default="english")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

   

# 🔹 Student Profile Model (Extra fields for Students)
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_name = models.CharField(max_length=100, unique=True)
    student_name = models.CharField(max_length=150)

    father_name = models.CharField(max_length=100, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)

    BOARD_CHOICES = [
        ("UP BOARD", "UP BOARD"),
        ("CBSE BOARD", "CBSE BOARD"),
        ("ICSE BOARD", "ICSE BOARD"),
        ("MAHARASHTRA BOARD", "MAHARASHTRA BOARD"),
        ("ODISHA BOARD", "ODISHA BOARD"),
    ]
    board = models.CharField(max_length=50, choices=BOARD_CHOICES, blank=True, null=True)

    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(6, 13)]
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True, null=True)

    # multiple subjects stored as CSV
    subject = models.CharField(max_length=200, blank=True, null=True)

    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.unique_name} - Student"
    # Teacher extra fields
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)

    # Parent extra fields
    child_name = models.CharField(max_length=150, blank=True, null=True)
    relation = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("user", "unique_name")

    def __str__(self):
        return f"{self.unique_name} ({self.role})"
