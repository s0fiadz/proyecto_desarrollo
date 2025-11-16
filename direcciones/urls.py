from django.urls import path
from direcciones import views


direcciones_urlpatterns = [
    # PÁGINA PRINCIPAL (masterpage con métricas)
    path('dashboard/', views.dashboard_direccion, name='dashboard_direccion'),
    
    # 🆕 NUEVA URL - LISTA DE INCIDENCIAS
    path('dashboard/incidencias/', views.lista_incidencias_direccion, name='lista_incidencias_direccion'),
    
    # 🆕 NUEVA URL - DEPARTAMENTOS ASIGNADOS
    path('dashboard/departamentos/', views.departamentos_direccion, name='departamentos_direccion'),
    
    # DETALLE DE INCIDENCIA (ya existe)
    path('dashboard/incidencia/<int:id>/', views.ver_incidencia_direccion, name='ver_incidencia_direccion'),
    
    # LAS OTRAS URLs (gestión de direcciones - para SECPLA)
    path('main_direccion/', views.main_direccion, name='main_direccion'),
    path('crear_direccion/', views.crear_direccion, name='crear_direccion'),
    path('guardar_direccion/', views.guardar_direccion, name='guardar_direccion'),
    path('ver_direccion/<id_direccion>/', views.ver_direccion, name='ver_direccion'),
    path('editar_direccion/', views.editar_direccion, name='editar_direccion'),
    path('editar_direccion/<id_direccion>/', views.editar_direccion, name='editar_direccion'),
    path('bloquear_desbloquear_direccion/<int:id_direccion>/', views.bloquear_desbloquear_direccion, name='bloquear_desbloquear_direccion'),
    path('direcciones_bloqueadas/', views.main_direcciones_bloqueadas, name='main_direcciones_bloqueadas'),
    path('asignar_encargado/<int:id_direccion>/', views.asignar_encargado, name='asignar_encargado'),
]