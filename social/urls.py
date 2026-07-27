from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Zugangscode-basierter Zugriff (ohne Account)
    path('access/<uuid:code>/', views.access_world, name='access_world'),
    path('world/<int:world_id>/codes/create/', views.create_access_code, name='create_access_code'),
    path('world/<int:world_id>/codes/manage/', views.manage_access_codes, name='manage_access_codes'),
    path('code/<int:code_id>/deactivate/', views.deactivate_code, name='deactivate_code'),
    
    # Kommentare (ohne Account)
    path('world/<int:world_id>/comment/add/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
