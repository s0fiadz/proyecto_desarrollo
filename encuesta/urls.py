from django.urls import path
from . import views

# Sin app_name



encuesta_urlpatterns = [
    path('', views.encuesta_list, name='encuesta_list'),
    path('crear/', views.encuesta_create, name='encuesta_create'),
    path('ver/<int:id>/', views.encuesta_view, name='encuesta_view'),
    path('editar/<int:id>/', views.encuesta_edit, name='encuesta_edit'),
    path('bloquear/<int:id>/', views.encuesta_toggle, name='encuesta_toggle'),
    path('eliminar-pregunta/<int:id_pregunta>/', views.eliminar_pregunta, name='eliminar_pregunta'),
]