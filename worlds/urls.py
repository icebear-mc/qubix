from django.urls import path
from . import views

urlpatterns = [
    path('', views.world_list, name='world_list'),
    path('world/create/', views.world_create, name='world_create'),
    path('world/<int:pk>/', views.world_detail, name='world_detail'),
    path('world/<int:pk>/edit/', views.world_edit, name='world_edit'),
    path('world/<int:pk>/delete/', views.world_delete, name='world_delete'),
    
    # Element URLs
    path('world/<int:world_pk>/element/<str:element_type>/create/', views.element_create, name='element_create'),
    path('element/<int:pk>/', views.element_detail, name='element_detail'),
    path('element/<int:pk>/edit/', views.element_edit, name='element_edit'),
    path('element/<int:pk>/delete/', views.element_delete, name='element_delete'),
    
    # Map view
    path('map/<int:pk>/', views.map_view, name='map_view'),
]
