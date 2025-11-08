from django.shortcuts import render
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Incidencia, DatosVecino, ArchivosMultimedia, RegistrosRespuestas
from encuesta.models import Encuesta, Preguntas, TipoIncidencia
from django.core.paginator import Paginator
from cuadrillas.models import Cuadrilla
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models import Q
from registration.models import Profile
from departamento.models import Departamento

def es_territorial(user):
    return user.groups.filter(name='Territorial').exists() or user.groups.filter(id=4).exists()

def es_territorial_o_admin(user):
    return user.groups.filter(id=1).exists() or user.groups.filter(id=4).exists()

@login_required
def main_tipo_incidencia(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')
    if profile.group_id ==1:
        return render(request, 'incidencia/main_tipo_incidencia.html')
    else:
        return redirect('logout')

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def main_territorial(request):
    return render(request, 'incidencia/main_territorial.html')

@login_required
@user_passes_test(es_territorial_o_admin, login_url='/accounts/login/')
def incidencia_list(request):
    incidencias = Incidencia.objects.filter(id_territorial=request.user)

    search_query = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    ordenar = request.GET.get('ordenar', 'id_asc')

    if search_query:
        incidencias = incidencias.filter(direccion__icontains=search_query)
    if estado:
        incidencias = incidencias.filter(estado=estado)
    if prioridad:
        incidencias = incidencias.filter(prioridad=prioridad)

    if ordenar == 'id_desc':
        incidencias = incidencias.order_by('-id_incidencia')
    elif ordenar == 'direccion_asc':
        incidencias = incidencias.order_by('direccion')
    elif ordenar == 'direccion_desc':
        incidencias = incidencias.order_by('-direccion')
    else:
        incidencias = incidencias.order_by('id_incidencia')

    paginator = Paginator(incidencias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'incidencias_listado': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'estado': estado,
        'prioridad': prioridad,
        'ordenar': ordenar,
    }

    return render(request, 'incidencia/incidencia_list.html', context)

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def incidencia_create(request):
    encuestas = Encuesta.objects.filter(activo=True)
    departamentos = Departamento.objects.filter(state='Activo')

    if request.method == 'POST':
        try:
            incidencia = Incidencia(
                id_encuesta_id=request.POST['id_encuesta'],
                id_territorial=request.user,
                descripcion=request.POST['descripcion'],
                departamento_id=request.POST['departamento'],
                direccion_incidente=request.POST.get('direccion_incidente', ''),
                lateral=request.POST.get('lateral', ''),
                longitud=request.POST.get('longitud', ''),
                prioridad=request.POST['prioridad'],
                estado='abierta'
            )
            incidencia.save()
            
            datos_vecino = DatosVecino(
                id_incidencia=incidencia,
                id_encuesta_id=request.POST['id_encuesta'],
                nombre=request.POST['nombre_vecino'],
                apellido=request.POST['apellido_vecino'],
                correo=request.POST.get('correo_vecino', ''),
                direccion_vicina=request.POST['direccion_vecino'],
                rat=request.POST.get('rat', '')
            )
            datos_vecino.save()
            
            encuesta_seleccionada = Encuesta.objects.get(id_encuesta=request.POST['id_encuesta'])
            preguntas = Preguntas.objects.filter(id_encuesta=encuesta_seleccionada)
            
            for pregunta in preguntas:
                respuesta_key = f'respuesta_{pregunta.id_preguntas}'
                if respuesta_key in request.POST:
                    RegistrosRespuestas.objects.create(
                        id_preguntas=pregunta,
                        id_incidencia=incidencia,
                        respuesta=request.POST[respuesta_key]
                    )

            archivos = request.FILES.getlist('archivos_multimedia')
            for archivo in archivos:
                tipo = determinar_tipo_archivo(archivo.name)
                ArchivosMultimedia.objects.create(
                    id_incidencia=incidencia,
                    tipo_archivo=tipo,
                    archivo=archivo,
                    descripcion=request.POST.get('descripcion_archivo', '')
                )
            
            return redirect('incidencia:incidencia_list')
            
        except Exception as e:
            return render(request, 'incidencia/incidencia_create.html', {
                'encuestas': encuestas,
                'departamentos':departamentos,
                'error': f'Error al crear incidencia: {str(e)}'
            })
    
    return render(request, 'incidencia/incidencia_create.html', {
        'encuestas': encuestas, 'departamentos':departamentos
    })

def determinar_tipo_archivo(nombre_archivo):
    extension = nombre_archivo.lower().split('.')[-1]
    if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
        return 'imagen'
    elif extension in ['mp4', 'avi', 'mov', 'wmv']:
        return 'video'
    elif extension in ['mp3', 'wav', 'ogg']:
        return 'audio'
    elif extension in ['pdf', 'doc', 'docx', 'txt']:
        return 'documento'
    else:
        return 'otro'

@login_required
@user_passes_test(es_territorial_o_admin, login_url='/accounts/login/')
def incidencia_view(request, id):
    incidencia = get_object_or_404(Incidencia, id_incidencia=id, id_territorial=request.user)
    datos_vecino = get_object_or_404(DatosVecino, id_incidencia=incidencia)
    archivos = ArchivosMultimedia.objects.filter(id_incidencia=incidencia)
    respuestas = RegistrosRespuestas.objects.filter(id_incidencia=incidencia)
    
    return render(request, 'incidencia/incidencia_view.html', {
        'incidencia': incidencia,
        'datos_vecino': datos_vecino,
        'archivos': archivos,
        'respuestas': respuestas
    })



def get_preguntas_encuesta(request):
    id_encuesta = request.GET.get('id_encuesta')
    preguntas = Preguntas.objects.filter(id_encuesta_id=id_encuesta)
    data = [{'id_preguntas': p.id_preguntas, 'pregunta': p.pregunta} for p in preguntas]
    return JsonResponse(data, safe=False)

#-------------------SUPERUSUARIO VIEWS-------------------#
@login_required
def tipo_incidencia_create(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')

    if profile.group_id == 1:
        if request.method == 'POST':
            nombre = request.POST.get('nombre', '').strip()
            if nombre:
                TipoIncidencia.objects.create(nombre=nombre)
                return redirect('incidencia:tipo_incidencia_list')
            else:
                error = "Debe ingresar un nombre para el tipo de incidencia"
                return render(request, 'incidencia/tipo_incidencia_create.html', {'error': error})
        return render(request, 'incidencia/tipo_incidencia_create.html')
    else:
        return redirect('logout')

@login_required
def tipo_incidencia_list(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')
    if profile.group_id ==1:
        tipos = TipoIncidencia.objects.all()
        return render(request, 'incidencia/tipo_incidencia_list.html', {'tipos': tipos})
    else:
        return redirect('logout')

@login_required
def incidencia_list_secpla(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    incidencias_listado = Incidencia.objects.select_related(
        'departamento__direccion'
    ).all()

    total_incidencias = incidencias_listado.count()
    total_abiertas = incidencias_listado.filter(estado='abierta').count()
    total_proceso = incidencias_listado.filter(estado='proceso').count()
    total_finalizadas = incidencias_listado.filter(estado='finalizada').count()
    total_cerradas = incidencias_listado.filter(estado='cerrada').count()
    total_rechazadas = incidencias_listado.filter(estado='rechazada').count()
    total_derivadas = incidencias_listado.filter(estado='derivada').count()

    search_query = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    ordenar = request.GET.get('ordenar', 'id_asc')

    if search_query:
        incidencias_listado = incidencias_listado.filter(
            direccion_incidente__icontains=search_query
        )

    if estado:
        incidencias_listado = incidencias_listado.filter(estado=estado)

    if prioridad:
        incidencias_listado = incidencias_listado.filter(prioridad=prioridad)

    if ordenar == 'id_desc':
        incidencias_listado = incidencias_listado.order_by('-id_incidencia')
    elif ordenar == 'direccion_asc':
        incidencias_listado = incidencias_listado.order_by('departamento__direccion__nombre')
    elif ordenar == 'direccion_desc':
        incidencias_listado = incidencias_listado.order_by('-departamento__direccion__nombre')
    else:
        incidencias_listado = incidencias_listado.order_by('id_incidencia')

    paginator = Paginator(incidencias_listado, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'incidencias_listado': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'estado': estado,
        'prioridad': prioridad,
        'ordenar': ordenar,
        'total_incidencias': total_incidencias,
        'total_abiertas': total_abiertas,
        'total_proceso': total_proceso,
        'total_finalizadas': total_finalizadas,
        'total_cerradas': total_cerradas,
        'total_rechazadas': total_rechazadas,
        'total_derivadas': total_derivadas,
    }

    return render(request, 'incidencia/incidencia_list_secpla.html', context)

@login_required
def incidencia_view_secpla(request, id_incidencia):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil de usuario no fue encontrado.')
        return redirect('login')

    if profile.group_id == 1:
        incidencia = get_object_or_404(Incidencia, id_incidencia=id_incidencia)
        datos_vecino = get_object_or_404(DatosVecino, id_incidencia=incidencia)
        archivos = ArchivosMultimedia.objects.filter(id_incidencia=incidencia)
        respuestas = RegistrosRespuestas.objects.filter(id_incidencia=incidencia)
    
        return render(request, 'incidencia/incidencia_view_secpla.html', {
            'incidencia': incidencia,
            'datos_vecino': datos_vecino,
            'archivos': archivos,
            'respuestas': respuestas
        })
    else:
        return redirect('logout')