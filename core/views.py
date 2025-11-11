from django.shortcuts import render
from django.conf import settings #importa el archivo settings
from django.contrib import messages #habilita la mesajería entre vistas
from django.contrib.auth.decorators import login_required #habilita el decorador que se niega el acceso a una función si no se esta logeado
from django.contrib.auth.models import Group, User # importa los models de usuarios y grupos
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator #permite la paqinación
from django.db.models import Avg, Count, Q #agrega funcionalidades de agregación a nuestros QuerySets
from django.http import (HttpResponse, HttpResponseBadRequest,
                        HttpResponseNotFound, HttpResponseRedirect) #Salidas alternativas al flujo de la aplicación se explicará mas adelante
from django.shortcuts import redirect, render #permite renderizar vistas basadas en funciones o redireccionar a otras funciones
from django.template import RequestContext # contexto del sistema
from django.views.decorators.csrf import csrf_exempt #decorador que nos permitira realizar conexiones csrf
from incidencia.models import Incidencia
from registration.models import Profile #importa el modelo profile, el que usaremos para los perfiles de usuarios

# Create your views here.
def home(request):
    return redirect('login')

@login_required
def pre_check_profile(request):
    #por ahora solo esta creada pero aún no la implementaremos
    pass


@login_required
def check_profile(request):
    if request.user.is_superuser or request.user.groups.filter(id=1).exists():
        return redirect('main_admin')
    elif request.user.groups.filter(id=2).exists():
        return redirect('dashboard_direccion') 
    elif request.user.groups.filter(id=4).exists():
        return redirect('/incidencia/')
    elif request.user.groups.filter(id=3).exists():
        return redirect('incidencia_list_derivar')
    elif request.user.groups.filter(id=5).exists():
        return redirect('dashboard_cuadrilla') 

    else:
        return redirect('main_admin')

#funcion temporal
@login_required
def main_admin(request):  
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()    
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')              
        return redirect('login')
    if profile.group_id == 1:    
        incidencias_listado = Incidencia.objects.select_related('departamento__direccion').all()
        cantidad_activos=User.objects.filter(is_active=True).count()
        total_incidencias = incidencias_listado.count()
        total_abiertas = incidencias_listado.filter(estado='abierta').count()
        total_proceso = incidencias_listado.filter(estado='proceso').count()
        total_finalizadas = incidencias_listado.filter(estado='finalizada').count()
        total_cerradas = incidencias_listado.filter(estado='cerrada').count()
        total_rechazadas = incidencias_listado.filter(estado='rechazada').count()
        total_derivadas = incidencias_listado.filter(estado='derivada').count()
        contexto = {
            'cantidad_activos': cantidad_activos,
            'total_incidencias': total_incidencias,
            'total_abiertas': total_abiertas,
            'total_proceso': total_proceso,
            'total_finalizadas': total_finalizadas,
            'total_cerradas': total_cerradas,
            'total_rechazadas': total_rechazadas,
            'total_derivadas': total_derivadas,
        }
        template_name = 'core/main_admin.html'
        return render(request,template_name, contexto)
    else:
        messages.add_message(request, messages.INFO, 'No tiene permisos para ver esta página')              
        return redirect('logout')