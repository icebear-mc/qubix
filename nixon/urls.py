from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.nixon_chat, name='nixon_chat'),
    path('chat/<int:world_pk>/', views.nixon_chat, name='nixon_chat_world'),
    path('api/message/', views.nixon_send_message, name='nixon_send_message'),
]
