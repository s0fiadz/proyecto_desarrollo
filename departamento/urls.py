from django.urls import path
from . import views

departamento_urlpatterns = [
    path('main_departamento/', views.main_departamento, name='main_departamento'),
    path('crear/', views.crear_departamento, name='crear_departamento'),
    path('editar/<int:id>/', views.editar_departamento, name='editar_departamento'),
    path('ver/<int:id>/', views.ver_departamento, name='ver_departamento'),
    path('bloquear_desbloquear/<int:id>/', views.bloquear_desbloquear_departamento, name='bloquear_desbloquear_departamento'),
    path('departamento_bloqueado/', views.main_departamento_bloqueado, name='main_departamento_bloqueado'),
    path('main_departamento/', views.main_departamento, name='main_departamento'),
    path('guardar_departamento/', views.guardar_departamento, name='guardar_departamento'),
    path('asignar_encargado/<int:id_departamento>/', views.asignar_encargado_depto, name='asignar_encargado'),
]
