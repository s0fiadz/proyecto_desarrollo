from django.urls import path
from . import views

departamento_urlpatterns = [
    path('main_departamento/', views.main_departamento, name='main_departamento'),
    path('crear/', views.crear_departamento, name='crear_departamento'),
    path('editar/<int:id>/', views.editar_departamento, name='editar_departamento'),
    path('ver/<int:id>/', views.ver_departamento, name='ver_departamento'),
    path('bloquear_desbloquear/<int:id>/', views.bloquear_desbloquear_departamento, name='bloquear_desbloquear_departamento'),
    path('departamento_bloqueado/', views.main_departamento_bloqueado, name='main_departamento_bloqueado'),
    path('guardar_departamento/', views.guardar_departamento, name='guardar_departamento'),
    path('asignar_encargado/<int:id_departamento>/', views.asignar_encargado_depto, name='asignar_encargado'),

    #  Listado de incidencias
    path('departamento/', views.incidencia_list_derivar, name='incidencia_list_derivar'),

    #  Cambiar estado de una incidencia (CORREGIDO)
    path('departamento/<int:id>/cambiar_estado/', views.cambiar_estado_incidencia, name='cambiar_estado_incidencia'),

    #  Derivar incidencia a cuadrilla (CORREGIDO)
    path('departamento/<int:id>/derivar/', views.derivar_cuadrilla, name='derivar_cuadrilla'),
    path('departamento/incidencia/<int:id>/', views.ver_incidencia_departamento, name='ver_incidencia_departamento'),
]