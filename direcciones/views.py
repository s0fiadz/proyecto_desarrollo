from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.shortcuts import redirect, render, get_object_or_404
from registration.models import Profile
from direcciones.models import Direccion, encargado_direccion
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from incidencia.models import Incidencia, DatosVecino, ArchivosMultimedia, RegistrosRespuestas
from django.contrib.auth.decorators import user_passes_test
from cuadrillas.models import Registro_cierre
from departamento.models import Departamento 


#----------------------------------------------------DASHBOARD DIRECCIÓN------------------------------------------------------------------------------
def es_encargado_direccion(user):
    return user.groups.filter(id=2).exists()

def filtrar_incidencias_por_estado(request, incidencias: QuerySet) -> QuerySet:
    estado_filtro = request.GET.get('estado', None)
    if estado_filtro:
        if any(estado_filtro == e[0] for e in Incidencia.ESTADOS):
            return incidencias.filter(estado=estado_filtro)
    return incidencias

def ordenar_incidencias(request, incidencias: QuerySet) -> QuerySet:
    orden = request.GET.get('ordenar', 'recientes')
    if orden == 'antiguas':
        return incidencias.order_by('fecha_creacion')
    if orden == 'prioridad':
        return incidencias.order_by('-prioridad')
    return incidencias.order_by('-fecha_creacion')

# TABLA  DE INCIDENCIAS
@login_required
@user_passes_test(es_encargado_direccion, login_url='/accounts/login/')
def lista_incidencias_direccion(request):
    try:
        encargado = encargado_direccion.objects.get(usuario=request.user)
        direccion_usuario = encargado.direccion
        id_direccion = direccion_usuario.id_direccion
    except encargado_direccion.DoesNotExist:
        messages.error(request, 'Usted no está asignado a ninguna dirección.')
        return render(request, 'direcciones/lista_incidencias.html', {
            'error': True,
            'estados': Incidencia.ESTADOS
        })

    # Buscar incidencias que pertenecen a departamentos de esta dirección
    incidencias_listado = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion
    ).select_related('departamento')

    # filtros y ordenamientos
    incidencias_listado = filtrar_incidencias_por_estado(request, incidencias_listado)
    incidencias_listado = ordenar_incidencias(request, incidencias_listado)

    # Paginación
    paginator = Paginator(incidencias_listado, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params = query_params.urlencode()

    context = {
        'page_obj': page_obj,
        'query_params': query_params,
        'estados': Incidencia.ESTADOS,
        'estado_seleccionado': request.GET.get('estado', ''),
        'orden_seleccionado': request.GET.get('ordenar', 'recientes'),
        'direccion_usuario': direccion_usuario
    }
   
    return render(request, 'direcciones/lista_incidencias.html', context)

#  MÉTRICAS (PÁGINA PRINCIPAL)
@login_required
@user_passes_test(es_encargado_direccion, login_url='/accounts/login/')
def dashboard_direccion(request):
    try:
        encargado = encargado_direccion.objects.get(usuario=request.user)
        direccion_usuario = encargado.direccion
        id_direccion = direccion_usuario.id_direccion
    except encargado_direccion.DoesNotExist:
        messages.error(request, 'Usted no está asignado a ninguna dirección.')
        return render(request, 'direcciones/masterpage.html', {'error': True})


    total_incidencias = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion
    ).count()
    
    incidencias_abiertas = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='abierta'
    ).count()
    
    incidencias_proceso = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='proceso'
    ).count()
    
    incidencias_finalizadas = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='finalizada'
    ).count()
    
    incidencias_derivadas = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='derivada'
    ).count()
    
    incidencias_rechazadas = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='rechazada'
    ).count()
    
    incidencias_cerradas = Incidencia.objects.filter(
        departamento__direccion_id=id_direccion,
        estado='cerrada'
    ).count()

    context = {
        'direccion_usuario': direccion_usuario,
        'total_incidencias': total_incidencias,
        'incidencias_abiertas': incidencias_abiertas,
        'incidencias_proceso': incidencias_proceso,
        'incidencias_finalizadas': incidencias_finalizadas,
        'incidencias_derivadas': incidencias_derivadas,
        'incidencias_rechazadas': incidencias_rechazadas,
        'incidencias_cerradas': incidencias_cerradas,
    }

    return render(request, 'direcciones/masterpage.html', context)

@login_required
@user_passes_test(es_encargado_direccion, login_url='/accounts/login/')
def ver_incidencia_direccion(request, id):
    try:
        encargado = encargado_direccion.objects.get(usuario=request.user)
        id_direccion = encargado.direccion.id_direccion
    except encargado_direccion.DoesNotExist:
        messages.error(request, 'No tiene dirección asignada.')
        return redirect('dashboard_direccion')

    incidencia = get_object_or_404(
        Incidencia,
        id_incidencia=id,
        departamento__direccion_id=id_direccion
    )

    datos_vecino = get_object_or_404(DatosVecino, id_incidencia=incidencia)
    archivos = ArchivosMultimedia.objects.filter(id_incidencia=incidencia)
    respuestas = RegistrosRespuestas.objects.filter(id_incidencia=incidencia)
    evidencias = Registro_cierre.objects.filter(incidencia=incidencia)

    return render(request, 'direcciones/ver_incidencia_direccion.html', {
        'incidencia': incidencia,
        'datos_vecino': datos_vecino,
        'archivos': archivos,
        'respuestas': respuestas,
        'evidencias': evidencias,
    })

# DEPARTAMENTOS ASIGNADOS
@login_required
@user_passes_test(es_encargado_direccion, login_url='/accounts/login/')
def departamentos_direccion(request):
    try:
        encargado = encargado_direccion.objects.get(usuario=request.user)
        direccion_usuario = encargado.direccion
    except encargado_direccion.DoesNotExist:
        messages.error(request, 'Usted no está asignado a ninguna dirección.')
        return render(request, 'direcciones/departamentos_direccion.html', {'error': True})


    departamentos = Departamento.objects.filter(direccion=direccion_usuario)
    
    context = {
        'direccion_usuario': direccion_usuario,
        'departamentos': departamentos,
    }
    return render(request, 'direcciones/departamentos_direccion.html', context)

#----------------------------------------------------------------------------------------------------------------------------------

@login_required
def main_direccion(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('login')

    if profile.group_id == 1:
        search_query = request.GET.get('search', '')
        ordenar=request.GET.get('ordenar', 'alfabetico')
        direccion_listado = Direccion.objects.filter(state=True).order_by('nombre_direccion')

        if search_query:
            direccion_listado = direccion_listado.filter(nombre_direccion__icontains=search_query)
        if ordenar == 'alfabetico':
            direccion_listado = direccion_listado.order_by('nombre_direccion')
        elif ordenar == 'alfabetico_desc':
            direccion_listado = direccion_listado.order_by('-nombre_direccion')
        elif ordenar == 'id_asc':
            direccion_listado = direccion_listado.order_by('id_direccion')
        elif ordenar == 'id_desc':
            direccion_listado = direccion_listado.order_by('-id_direccion')
        
        paginator = Paginator(direccion_listado, 5)
        page_number = request.GET.get('page')
        page_object = paginator.get_page(page_number)

        direccion_listado = paginator.get_page(page_number)
        template_name = 'direcciones/main_direccion.html'
        return render(request, template_name,{'direccion_listado': page_object,'search_query': search_query, 'ordenar': ordenar})
    else:
        return redirect('logout')

@login_required
def crear_direccion(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        template_name = 'direcciones/crear_direccion.html'
        return render(request,template_name)
    else:
        return redirect('logout')

@login_required
def guardar_direccion(request):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        if request.method == 'POST':
            nombre_direccion = request.POST.get('nombre_direccion')
            state = True if request.POST.get('state') == 'on' else False
            if nombre_direccion == '':
                messages.add_message(request, messages.INFO, 'Todos los campos son obligatorios.')
                return redirect('crear_direccion')
            if Direccion.objects.filter(nombre_direccion=nombre_direccion).exists():
                messages.add_message(request, messages.INFO, 'El nombre de la dirección ya existe. Por favor, elija otro.')
                return redirect('crear_direccion')
            else:
                direccion_save = Direccion(nombre_direccion=nombre_direccion, state=state)
                direccion_save.save()
                messages.add_message(request, messages.INFO, 'Dirección creada con éxito.')
                return redirect('main_direccion')
        else:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_group_main')
    else:
        return redirect('logout')

@login_required
def bloquear_desbloquear_direccion(request, id_direccion):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')
    if profile.group_id == 1:
        try:
            direccion = Direccion.objects.get(pk=id_direccion)
            direccion.state = not direccion.state
            direccion.save()
            if direccion.state:
                messages.add_message(request, messages.INFO, f'La dirección {direccion.nombre_direccion} fue DESBLOQUEADA con éxito.')
            else:
                messages.add_message(request, messages.INFO, f'La dirección {direccion.nombre_direccion} fue BLOQUEADA con éxito.')
            return redirect(request.META.get('HTTP_REFERER', 'main_direccion'))
        except Direccion.DoesNoExist:
            messages.add_message(request, messages.INFO, 'La dirección no éxiste. ')
            return redirect('main_direccion')
    else:
        return redirect('logout')

@login_required
def main_direcciones_bloqueadas(request):
    try:
        profile=Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request,messages.INFO,'Hubo un error')
        return redirect('login')
    if profile.group_id == 1:
        direccion_bloqueada_listado= Direccion.objects.filter(state=False).order_by('nombre_direccion')
        template_name = 'direcciones/main_direcciones_bloqueadas.html'
        return render(request, template_name, {'direccion_bloqueada_listado': direccion_bloqueada_listado})
    else:
        return redirect('logout')
    
@login_required
def ver_direccion(request, id_direccion):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1: 
        try: 
            direccion_count = Direccion.objects.filter(pk=id_direccion).count()
            if direccion_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            direccion_data = Direccion.objects.get(pk=id_direccion)
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'direcciones/ver_direccion.html'
        return render(request,template_name,{'direccion_data':direccion_data})
    else:
        return redirect('logout')
    
@login_required
def editar_direccion(request,id_direccion=None):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        try:
            if request.method == 'POST' : 
                nombre_direccion = request.POST.get('nombre_direccion')
                state = request.POST.get('state')
                direccion_count = Direccion.objects.filter(pk=id_direccion).count()
                if direccion_count <= 0:
                    messages.add_message(request, messages.INFO, 'Hubo un error')
                    return redirect('check_profile')
                if nombre_direccion == '' or state == '':
                    messages.add_message(request, messages.INFO, 'Hubo un error')
                    return redirect('main_direccion')
                state_bool = True if state == 'True' else False
                Direccion.objects.filter(pk=id_direccion).update(nombre_direccion=nombre_direccion)
                Direccion.objects.filter(pk=id_direccion).update(state=state_bool)
                messages.add_message(request, messages.INFO, 'Direccion actualizada')
                return redirect('main_direccion')
        except:
            messages.add_message(request,messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        
        try:
            direccion_count = Direccion.objects.filter(pk=id_direccion).count()
            if direccion_count <= 0:
                messages.add_message(request, messages.INFO , 'Hubo un error')
                return redirect('check_profile')
            direccion_data = Direccion.objects.get(pk=id_direccion)
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'direcciones/editar_direccion.html'
        return render(request,template_name,{'direccion_data':direccion_data})
    else:
        return redirect('check_profile')
    

@login_required
def asignar_encargado(request, id_direccion):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con el perfil del usuario.')
        return redirect('check_profile')

    if profile.group_id == 1:
        try:
            direccion = get_object_or_404(Direccion, id_direccion=id_direccion)
            usuarios = User.objects.filter(groups__id=2, is_active=True).distinct().order_by('first_name', 'last_name')

            if request.method == 'POST':
                usuario_id = request.POST.get('usuario')
                if usuario_id:
                    try:
                        usuario = User.objects.get(id=usuario_id)
                    except User.DoesNotExist:
                        messages.error(request, 'Usuario no válido.')
                        return render(request, 'direcciones/asignar_encargado.html', {'direccion': direccion,'usuarios': usuarios})
                    encargado_existente = encargado_direccion.objects.filter(usuario=usuario).exclude(direccion=direccion).first()
                    if encargado_existente:
                        messages.error(
                            request,f'{usuario.get_full_name()} ya es encargado de la dirección "{encargado_existente.direccion.nombre_direccion}".')
                        return render(request, 'direcciones/asignar_encargado.html', {'direccion': direccion,'usuarios': usuarios})

                    #elimina si ya existe un encargado:
                    encargado_direccion.objects.filter(direccion=direccion).delete()
                    #asigna el nuevo:
                    encargado_direccion.objects.create(direccion=direccion, usuario=usuario)

                    messages.success(request, f'{usuario.get_full_name()} asignado a {direccion.nombre_direccion}.')
                    return redirect('main_direccion')

            return render(request, 'direcciones/asignar_encargado.html', {'direccion': direccion,'usuarios': usuarios})

        except Exception as e:
            messages.add_message(request, messages.INFO, f'Hubo un error: {str(e)}')
            return redirect('check_profile')

    else:
        return redirect('check_profile')