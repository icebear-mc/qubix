from django.urls import path
from . import views

urlpatterns = [
    path('users/search/', views.user_search, name='user_search'),
    path('friend/request/send/<str:username>/', views.friend_request_send, name='friend_request_send'),
    path('friend/requests/', views.friend_request_list, name='friend_request_list'),
    path('friend/request/<int:pk>/accept/', views.friend_request_accept, name='friend_request_accept'),
    path('friend/request/<int:pk>/decline/', views.friend_request_decline, name='friend_request_decline'),
    path('friends/', views.friend_list, name='friend_list'),
    path('friend/remove/<str:username>/', views.friend_remove, name='friend_remove'),
]
