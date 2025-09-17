# gamify/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("chatbot_api/", views.chatbot_api, name="chatbot_api"),
]
