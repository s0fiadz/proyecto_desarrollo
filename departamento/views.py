from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Departamento, EncargadoDepartamento
from registration.models import Profile
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from direcciones.models import Direccion
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from incidencia.models import Incidencia, DatosVecino, ArchivosMultimedia, RegistrosRespuestas
from cuadrillas.models import Cuadrilla
from django.contrib.auth.decorators import login_required, user_passes_test
from cuadrillas.models import Registro_cierre
from django.contrib.auth import logout

def filtrar_departamentos_por_direccion(request, departamentos: QuerySet) -> QuerySet:
    """Filtra el QuerySet de departamentos por la Dirección ID pasada en la URL (GET)."""
    direccion_id_filtro = request.GET.get('direccion_id')
    if direccion_id_filtro and direccion_id_filtro.isdigit():
        return departamentos.filter(direccion__pk=direccion_id_filtro)
    return departamentos

def ordenar_departamentos(request, departamentos: QuerySet) -> QuerySet:
    """Ordena el QuerySet de departamentos según el parámetro 'ordenar' de la URL (GET)."""
    orden = request.GET.get('ordenar')
    if orden == 'alfabeticamente':
        return departamentos.order_by('nombre_dpto')
    elif orden == 'direccion':
        return departamentos.order_by('direccion__nombre_direccion')
    return departamentos.order_by('nombre_dpto') 

@login_required
def main_departamento(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Hubo un error con su perfil')
        return redirect('login')

    if profile.group_id != 1:
        logout(request)
        return redirect('login')

    departamentos_list = Departamento.objects.filter(state='Activo').select_related('direccion', 'encargado')
    departamentos_list = filtrar_departamentos_por_direccion(request, departamentos_list)
    departamentos_list = ordenar_departamentos(request, departamentos_list)

    search_query = request.GET.get('search', None) 
    
    if search_query:
        departamentos_list = departamentos_list.filter(
            Q(nombre_dpto__icontains=search_query) |
            Q(direccion__nombre_direccion__icontains=search_query)
        )

    page = request.GET.get('page', 1) 
    try:
        per_page = int(request.GET.get('per_page', 8)) 
    except ValueError:
        per_page = 8
    
    paginator = Paginator(departamentos_list, per_page)
    
    try:
        departamentos = paginator.page(page)
    except PageNotAnInteger:
        departamentos = paginator.page(1)
    except EmptyPage:
        departamentos = paginator.page(paginator.num_pages)

    todas_las_direcciones = Direccion.objects.filter(state=True).order_by('nombre_direccion')
    
    query_params = request.GET.urlencode()
    query_params = '&'.join([f for f in query_params.split('&') if not f.startswith('page')])

    context = {
        'departamentos': departamentos, 
        'todas_las_direcciones': todas_las_direcciones,
        'direccion_id_seleccionada': request.GET.get('direccion_id'),
        'orden_seleccionado': request.GET.get('ordenar'),
        'search_query': search_query,
        'query_params': query_params,
    }
    
    template_name = 'departamento/main_departamento.html'
    return render(request, template_name, context)

@login_required
def crear_departamento(request):
    """Renderiza un formulario para crear un nuevo departamento"""
    direcciones = Direccion.objects.all()
    return render(request, 'departamento/crear_departamento.html', {'direcciones': direcciones})


@login_required
def guardar_departamento(request):
    """Procesa el POST para crear un nuevo departamento (similar a guardar_usuario en registration.views)"""
    if request.method != 'POST':
        messages.info(request, 'Método no permitido')
        return redirect('crear_departamento')

    nombre = request.POST.get('nombre_dpto', '')
    direccion_id = request.POST.get('direccion', '')


    if not nombre or not direccion_id:
        messages.error(request, "Todos los campos son obligatorios.")
        return redirect('crear_departamento')

    if Departamento.objects.filter(nombre_dpto__iexact=nombre).exists():
        messages.error(request, "Ya existe un departamento con ese nombre.")
        return redirect('crear_departamento')

    try:
        direccion_obj = Direccion.objects.get(pk=direccion_id)
    except Direccion.DoesNotExist:
        messages.error(request, "La dirección seleccionada no existe.")
        return redirect('crear_departamento')

    Departamento.objects.create(
        nombre_dpto=nombre,
        direccion=direccion_obj,
        encargado=request.user
    )

    messages.success(request, "Departamento creado con éxito.")
    print("Redirigiendo a main_departamento")
    return redirect('main_departamento')

@login_required
def bloquear_desbloquear_departamento(request, id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')

    if profile.group_id == 1:
        try:
            departamento = Departamento.objects.get(pk=id)
            # Toggle state
            if departamento.state == "Activo":
                departamento.state = "Bloqueado"
                messages.add_message(request, messages.INFO, f"El departamento {departamento.nombre_dpto} fue BLOQUEADO con éxito.")
            else:
                departamento.state = "Activo"
                messages.add_message(request, messages.INFO, f"El departamento {departamento.nombre_dpto} fue DESBLOQUEADO con éxito.")
            departamento.save()
            return redirect(request.META.get('HTTP_REFERER', 'main_departamento'))
        except Departamento.DoesNotExist:
            messages.add_message(request, messages.INFO, 'El departamento no existe.')
            return redirect('main_departamento')
    else:
        logout(request)
        return redirect('login')
    
@login_required
def main_departamento_bloqueado(request):
    try:
        profile=Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request,messages.INFO,'Hubo un error')
        return redirect('login')
    if profile.group_id == 1:
        departamento_bloqueado_listado = Departamento.objects.filter(state="Bloqueado").order_by('nombre_dpto')
        template_name = 'departamento/main_departamento_bloqueado.html'
        return render(request, template_name, {'departamento_bloqueado_listado': departamento_bloqueado_listado})
    else:
        logout(request)
        return redirect('login')

@login_required
def editar_departamento(request, id=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Exception:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')

    if profile.group_id == 1:
        if request.method == 'POST':
            try:
                nombre = request.POST.get('nombre_dpto', '').strip()
                direccion_id = request.POST.get('direccion', '').strip()

                departamento_count = Departamento.objects.filter(pk=id).count()
                if departamento_count <= 0:
                    messages.add_message(request, messages.INFO, 'Hubo un error')
                    return redirect('main_departamento')

                if nombre == '' or direccion_id == '':
                    messages.add_message(request, messages.INFO, 'Todos los campos son obligatorios.')
                    return redirect('editar_departamento', id=id)

                if Departamento.objects.filter(nombre_dpto__iexact=nombre).exclude(pk=id).exists():
                    messages.add_message(request, messages.INFO, 'Ya existe un departamento con ese nombre.')
                    return redirect('editar_departamento', id=id)

                try:
                    Direccion.objects.get(pk=direccion_id)
                except Direccion.DoesNotExist:
                    messages.add_message(request, messages.INFO, 'La dirección seleccionada no existe.')
                    return redirect('editar_departamento', id=id)
                except ValueError:
                    messages.add_message(request, messages.INFO, 'ID de dirección no válido.')
                    return redirect('editar_departamento', id=id)

                Departamento.objects.filter(pk=id).update(
                    nombre_dpto=nombre,
                    direccion_id=direccion_id
                )

                messages.add_message(request, messages.INFO, 'Datos actualizados')
                return redirect('main_departamento')
            except Exception:
                messages.add_message(request, messages.INFO, 'hubo un error')
                return redirect('main_departamento')

        # bloque get
        try:
            departamento_count = Departamento.objects.filter(pk=id).count()
            if departamento_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('main_departamento')
            departamento = Departamento.objects.get(pk=id)
            direcciones = Direccion.objects.all()
        except Exception:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            logout(request)
            return redirect('login')

        template_name = 'departamento/editar_departamento.html'
        return render(request, template_name, {'departamento': departamento, 'direcciones': direcciones})
    else:
        logout(request)
        return redirect('login')

#Funcion ver_departamento
@login_required
def ver_departamento(request, id=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        logout(request)
        return redirect('login')

    if profile.group_id == 1:
        departamento = get_object_or_404(Departamento, pk=id)

        template_name = 'departamento/ver_departamento.html'
        return render(request, template_name, {'departamento': departamento})
    else:
        logout(request)
        return redirect('login')
    
@login_required
def departamentos_json_list(request):

    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'Authentication failed'}, status=401) 

    if profile.group_id != 1:
        return JsonResponse({'error': 'Permission denied. Only administrators can access this resource.'}, status=403)
    
    departamentos_list = Departamento.objects.filter(state='Activo').select_related('direccion').order_by('nombre_dpto')

    search_query = request.GET.get('search', None) 
    
    if search_query:
        departamentos_list = departamentos_list.filter(
            Q(nombre_dpto__icontains=search_query) |
            Q(direccion__nombre_direccion__icontains=search_query)
        )

    page = request.GET.get('page', 1) 
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10
    
    paginator = Paginator(departamentos_list, per_page)
    
    try:
        departamentos = paginator.page(page)
    except PageNotAnInteger:
        departamentos = paginator.page(1)
    except EmptyPage:
        departamentos = paginator.page(paginator.num_pages)

    data = []
    for dpto in departamentos:
        data.append({
            'id_departamento': dpto.pk, 
            'nombre_departamento': dpto.nombre_dpto,
            'estado': dpto.state,
            'direccion': {
                'id_direccion': dpto.direccion.id_direccion,
                'nombre_direccion': dpto.direccion.nombre_direccion,
            }
        })
    response_data = {
        'total_registros': paginator.count,
        'total_paginas': paginator.num_pages,
        'pagina_actual': departamentos.number,
        'elementos_por_pagina': per_page, 
        'has_next': departamentos.has_next(),
        'has_previous': departamentos.has_previous(),
        'results': data
    }
    
    return JsonResponse(response_data)

@login_required
def asignar_encargado_depto(request, id_departamento):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error de autenticación.')
        return redirect('logout')

    if profile.group_id != 1:
        messages.info(request, 'No tiene permisos para realizar esta acción.')
        logout(request)
        return redirect('login')
    try:
        departamento = Departamento.objects.get(pk=id_departamento)
    except Departamento.DoesNotExist:
        messages.info(request, 'El departamento no existe.')
        return redirect('main_departamento')
    usuarios = (
        User.objects
        .filter(groups__id=3, is_active=True)
        .distinct()
        .order_by('first_name', 'last_name')
    )
    if request.method == 'POST':
        id_usuario = request.POST.get('usuario', '').strip()
        if not id_usuario:
            messages.info(request, 'Debe seleccionar un usuario.')
            return redirect('asignar_encargado_depto', id_departamento=id_departamento)
        try:
            usuario = User.objects.get(pk=id_usuario)
        except User.DoesNotExist:
            messages.info(request, 'El usuario seleccionado no existe.')
            return redirect('asignar_encargado_depto', id_departamento=id_departamento)
        if EncargadoDepartamento.objects.filter(departamento=departamento).exists():
            messages.info(request, f'El departamento "{departamento.nombre_dpto}" ya tiene un encargado asignado.')
            return redirect('main_departamento')
        if EncargadoDepartamento.objects.filter(usuario=usuario).exists():
            messages.info(request, f'El usuario "{usuario.username}" ya está asignado a otro departamento.')
            return redirect('main_departamento')
        EncargadoDepartamento.objects.create(departamento=departamento, usuario=usuario)
        messages.success(
            request,
            f'Se asignó correctamente a "{usuario.get_full_name() or usuario.username}" '
            f'como encargado del departamento "{departamento.nombre_dpto}".'
        )
        return redirect('main_departamento')
    template_name = 'departamento/asignar_encargado.html'
    context = {
        'departamento': departamento,
        'usuarios': usuarios
    }
    return render(request, template_name, context)


def es_departamento(user):
    return user.groups.filter(name='Departamento').exists() or user.groups.filter(id=3).exists()

@login_required
@user_passes_test(es_departamento, login_url='/accounts/login/')
def incidencia_list_derivar(request):
    # Obtener el departamento del usuario actual
    try:
        profile = Profile.objects.get(user=request.user)
        # Si el usuario es del grupo Departamento (id=3), buscar su departamento
        if profile.group_id == 3:
            # Buscar si el usuario es encargado de algún departamento
            try:
                encargado_depto = EncargadoDepartamento.objects.get(usuario=request.user)
                departamento_usuario = encargado_depto.departamento
                # Filtrar incidencias por el departamento del usuario
                incidencias = Incidencia.objects.filter(departamento=departamento_usuario)
                
            except EncargadoDepartamento.DoesNotExist:
                # Si no es encargado de ningún departamento, no mostrar incidencias
                incidencias = Incidencia.objects.none()
        
        # Si el usuario es de otro grupo (territorial, admin, etc.)
        else:
            # Mostrar todas las incidencias o filtrar según el grupo
            incidencias = Incidencia.objects.all()

    except Profile.DoesNotExist:
        incidencias = Incidencia.objects.none()

    # Aplicar filtros de búsqueda
    search_query = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    prioridad = request.GET.get('prioridad', '')
    ordenar = request.GET.get('ordenar', 'id_asc')

    if search_query:
        incidencias = incidencias.filter(direccion_incidente__icontains=search_query)
    
    if estado:
        incidencias = incidencias.filter(estado=estado)
    
    if prioridad:
        incidencias = incidencias.filter(prioridad=prioridad)

    # Ordenamiento
    if ordenar == 'id_desc':
        incidencias = incidencias.order_by('-id_incidencia')
    elif ordenar == 'direccion_asc':
        incidencias = incidencias.order_by('direccion_incidente')
    elif ordenar == 'direccion_desc':
        incidencias = incidencias.order_by('-direccion_incidente')
    else:
        incidencias = incidencias.order_by('id_incidencia')

    # Paginación
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

    return render(request, 'departamento/incidencia_list_derivar.html', context)

@login_required
def cambiar_estado_incidencia(request, id):
    incidencia = get_object_or_404(Incidencia, pk=id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Incidencia.ESTADOS):
            incidencia.estado = nuevo_estado
            incidencia.save()
            messages.success(request, f'Estado actualizado a "{nuevo_estado}".')
            return redirect('incidencia_list_derivar')
        else:
            messages.error(request, 'Estado no válido.')
    return render(request, 'departamento/cambiar_estado.html', {'incidencia': incidencia})

@login_required
def derivar_cuadrilla(request, id):
    incidencia = get_object_or_404(Incidencia, pk=id)
    cuadrillas = Cuadrilla.objects.all()
    
    if request.method == 'POST':
        cuadrilla_id = request.POST.get('cuadrilla')
        
        if cuadrilla_id:
            try:
                cuadrilla = Cuadrilla.objects.get(id_cuadrilla=cuadrilla_id)
                
                cuadrilla_anterior = incidencia.id_cuadrilla
                
                # Siempre permitir asignar/re-asignar cuadrilla
                incidencia.id_cuadrilla = cuadrilla
                incidencia.estado = 'derivada'
                incidencia.save()
                
                # Verificar que se guardó
                incidencia.refresh_from_db()
                
                if cuadrilla_anterior:
                    messages.success(request, f'✅ Incidencia #{incidencia.id_incidencia} re-derivada de {cuadrilla_anterior.nombre_cuadrilla} a {cuadrilla.nombre_cuadrilla}')
                else:
                    messages.success(request, f'✅ Incidencia #{incidencia.id_incidencia} derivada a {cuadrilla.nombre_cuadrilla}')
                    
                return redirect('incidencia_list_derivar')
                
            except Cuadrilla.DoesNotExist:
                messages.error(request, '❌ La cuadrilla seleccionada no existe')
            except Exception as e:
                messages.error(request, f'❌ Error al derivar: {str(e)}')
        else:
            messages.error(request, '⚠️ Debes seleccionar una cuadrilla')
    
    return render(request, 'departamento/derivar_cuadrilla.html', {
        'incidencia': incidencia,
        'cuadrillas': cuadrillas
    })

@login_required
@user_passes_test(es_departamento, login_url='/accounts/login/')
def ver_incidencia_departamento(request, id):
    try:
        encargado = EncargadoDepartamento.objects.get(usuario=request.user)
        departamento_id = encargado.departamento_id
    except EncargadoDepartamento.DoesNotExist:
        messages.error(request, 'No tiene dirección asignada.')
        return redirect('incidencia_list_derivar')

    incidencia = get_object_or_404(
        Incidencia,
        id_incidencia=id,
        departamento_id=departamento_id
    )

    datos_vecino = get_object_or_404(DatosVecino, id_incidencia=incidencia)
    archivos = ArchivosMultimedia.objects.filter(id_incidencia=incidencia)
    respuestas = RegistrosRespuestas.objects.filter(id_incidencia=incidencia)
    evidencias = Registro_cierre.objects.filter(incidencia=incidencia)  # 👈 AÑADIDO

    return render(request, 'departamento/ver_incidencia_departamento.html', {
        'incidencia': incidencia,
        'datos_vecino': datos_vecino,
        'archivos': archivos,
        'respuestas': respuestas,
        'evidencias': evidencias,  # 👈 AÑADIDO
    })