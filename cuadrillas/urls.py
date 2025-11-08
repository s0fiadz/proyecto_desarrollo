from django.urls import path
from cuadrillas import views

cuadrillas_urlpatterns = [
    # CUADRILLAS
    path('main_cuadrilla/', views.main_cuadrilla, name='main_cuadrilla'),
    path('crear_cuadrilla/', views.crear_cuadrilla, name='crear_cuadrilla'),
    path('guardar_cuadrilla/', views.guardar_cuadrilla, name='guardar_cuadrilla'),
    path('asignar_jefe_cuadrilla/<int:id_cuadrilla>/', views.asignar_jefe_cuadrilla, name='asignar_jefe_cuadrilla'),
    path('cuadrillas/asignar_departamento/<int:id_cuadrilla>/', views.asignar_departamento_cuadrilla, name='asignar_departamento_cuadrilla'),
    path('ver_cuadrillas/<id_cuadrilla>/', views.ver_cuadrillas, name='ver_cuadrillas'),
    path('editar_cuadrillas/',views.editar_cuadrillas, name= 'editar_cuadrillas'),
    path('editar_cuadrillas/<id_cuadrilla>/',views.editar_cuadrillas, name= 'editar_cuadrillas'),
    path('bloquear_cuadrilla/<id_cuadrilla>', views.bloquear_cuadrilla, name='bloquear_cuadrilla'),
    path('listar_cuadrillas_bloqueadas/', views.listar_cuadrillas_bloqueadas, name='listar_cuadrillas_bloqueadas'),
    path('desbloquear_cuadrilla/<int:id_cuadrilla>/', views.desbloquear_cuadrilla, name='desbloquear_cuadrilla'),
    path('dashboard/', views.dashboard_cuadrilla, name='dashboard_cuadrilla'),
    path('dashboard/incidencia/<int:id>/', views.ver_incidencia_cuadrilla, name='ver_incidencia_cuadrilla'),
    
    #OPERARIOS
    path('main_operario/', views.main_operario, name='main_operario'),
    path('cambiar_cargo/<int:miembro_id>/', views.cambiar_cargo, name='cambiar_cargo'),
    path('ver_operario/<usuario_id>/', views.ver_operario, name='ver_operario'),
    path('bloquear_operario/<usuario_id>/', views.bloquear_operario, name='bloquear_operario'),
    path('listar_operarios_bloqueados/', views.listar_operarios_bloqueados, name='listar_operarios_bloqueados'),
    path('desbloquear_operario/<int:usuario_id>/', views.desbloquear_operario, name='desbloquear_operario'),
]
