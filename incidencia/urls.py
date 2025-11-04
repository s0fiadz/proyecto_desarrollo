from django.urls import path
from . import views

app_name = 'incidencia'

incidencia_urlpatterns = [
    path('', views.main_territorial, name='main_territorial'),
    path('lista/', views.incidencia_list, name='incidencia_list'),
    path('crear/', views.incidencia_create, name='incidencia_create'),
    path('ver/<int:id>/', views.incidencia_view, name='incidencia_view'),
    path('cambiar-estado/<int:id>/', views.cambiar_estado_incidencia, name='cambiar_estado'),
    path('get-preguntas/', views.get_preguntas_encuesta, name='get_preguntas'),
    path('derivar/<int:id>/', views.derivar_cuadrilla, name='derivar_cuadrilla'),
    path('tipo-incidencia/crear/', views.tipo_incidencia_create, name='tipo_incidencia_create'),
    path('tipo-incidencia/lista/', views.tipo_incidencia_list, name='tipo_incidencia_list'),
    path('main-tipo-incidencia/', views.main_tipo_incidencia, name='main_tipo_incidencia'),
    path('incidencia_list_secpla', views.incidencia_list_secpla, name='incidencia_list_secpla'),
    path('ver-secpla/<int:id_incidencia>/', views.incidencia_view_secpla, name='incidencia_view_secpla'),
]