

# Register your models here.
from django.contrib import admin
from .models import Subject, Course, Lesson, Quiz, Question, Choice

admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
