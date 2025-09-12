from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify

class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    board = models.CharField(max_length=50, default='CBSE')
    class_level = models.CharField(max_length=50)  # e.g., "Class 9"

    def __str__(self):
        return f"{self.name} ({self.class_level})"

class Course(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to='course_covers/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.subject.name}-{self.title}"
            self.slug = slugify(base)[:200]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    content_text = models.TextField(blank=True)
    content_file = models.FileField(upload_to='lessons/', null=True, blank=True)
    duration = models.PositiveIntegerField(default=5, help_text="minutes")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"

class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    time_limit = models.PositiveIntegerField(null=True, blank=True, help_text='seconds')
    total_marks = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (('mcq','MCQ'), ('fill','Fill'), ('match','Match'), ('tf','True/False'))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    qtype = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq')
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.text[:80]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:80]
