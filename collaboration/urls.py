from django.urls import path
from . import views

urlpatterns = [
    path('world/<int:world_pk>/invite/', views.world_invite_collaborator, name='world_invite_collaborator'),
    path('invite/<int:pk>/accept/', views.collaborator_invite_accept, name='collaborator_invite_accept'),
    path('invite/<int:pk>/decline/', views.collaborator_invite_decline, name='collaborator_invite_decline'),
    path('world/<int:world_pk>/collaborators/', views.world_collaborators, name='world_collaborators'),
    path('collaborator/<int:pk>/remove/', views.collaborator_remove, name='collaborator_remove'),
]
