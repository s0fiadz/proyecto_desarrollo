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
]