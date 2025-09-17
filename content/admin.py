from django.contrib import admin
from .models import Subject, Lesson, Topic, Quiz, Question, Choice



# Inline for Topic in Lesson admin
class TopicInline(admin.TabularInline):
	model = Topic
	extra = 1

class LessonAdmin(admin.ModelAdmin):
	inlines = [TopicInline]
	list_display = ('title', 'subject', 'order', 'duration')
	fields = ('subject', 'title', 'order', 'content_text', 'duration')  # removed content_file

admin.site.register(Subject)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Topic)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
