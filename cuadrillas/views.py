from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from registration.models import Profile, User
from cuadrillas.models import Cuadrilla, Miembro_cuadrilla
from departamento.models import Departamento
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from incidencia.models import Incidencia, DatosVecino, ArchivosMultimedia, RegistrosRespuestas
from .models import Registro_cierre
from .forms import RegistroCierreForm
from datetime import date
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import logout



# Create your views here.
# TODO LO DE CUADRILLA
@login_required
def main_cuadrilla(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('login')

    if profile.group_id == 1:
        cuadrilla_listado = Cuadrilla.objects.filter(state=True).order_by('nombre_cuadrilla').prefetch_related('usuarios')
        
        #Búsqueda por nombre
        busqueda = request.GET.get('busqueda', '')
        if busqueda:
            cuadrilla_listado = cuadrilla_listado.filter(
                Q(nombre_cuadrilla__icontains=busqueda) |
                Q(jefe_cuadrilla__usuario__first_name__icontains=busqueda) |
                Q(jefe_cuadrilla__usuario__last_name__icontains=busqueda)
            )
        #Filtro por departamento
        departamento_id = request.GET.get('departamento', '')
        if departamento_id:
            cuadrilla_listado = cuadrilla_listado.filter(departamento_id=departamento_id)
        #Orden alfabético
        orden = request.GET.get('orden', 'asc')
        if orden == 'desc':
            cuadrilla_listado = cuadrilla_listado.order_by('-nombre_cuadrilla')
        else:  # asc
            cuadrilla_listado = cuadrilla_listado.order_by('nombre_cuadrilla')
        #Paginación 
        paginator = Paginator(cuadrilla_listado, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        departamentos = Departamento.objects.all()
        template_name = 'cuadrillas/main_cuadrilla.html'
        context = {
            'page_obj': page_obj,
            'departamentos': departamentos, 
            'busqueda': busqueda,  
            'departamento_seleccionado': departamento_id, 
            'orden_seleccionado': orden, 
        }
        return render(request, template_name, context)
    else:
        logout(request)
        return redirect('login')
    

@login_required
def crear_cuadrilla(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error al obtener el perfil del usuario.')
        return redirect('check_profile')

    if profile.group_id == 1:
        operarios_disponibles = User.objects.filter(groups__id=5).exclude(
            id__in=Miembro_cuadrilla.objects.values_list('usuario_id', flat=True)
        ).order_by('first_name')

        if not operarios_disponibles.exists():
            messages.warning(request, 'No hay operadores disponibles. Todos ya pertenecen a una cuadrilla.')
            return redirect('main_cuadrilla')

        context = {'operarios_listado': operarios_disponibles}
        return render(request, 'cuadrillas/crear_cuadrilla.html', context)

    else:
        logout(request)
        return redirect('login')


@login_required
def guardar_cuadrilla(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con el perfil del usuario.')
        return redirect('check_profile')

    if profile.group_id == 1:
        if request.method == 'POST':
            nombre_cuadrilla = request.POST.get('nombre_cuadrilla')
            cuadrillas_ids = request.POST.getlist('cuadrillas')
            state = request.POST.get('state') == 'on'

            if not nombre_cuadrilla:
                messages.error(request, 'El nombre de la cuadrilla es obligatorio.')
                return redirect('crear_cuadrilla')

            if Cuadrilla.objects.filter(nombre_cuadrilla=nombre_cuadrilla).exists():
                messages.info(request, 'El nombre de la cuadrilla ya existe. Elija otro.')
                return redirect('crear_cuadrilla')

            # Crear la cuadrilla
            cuadrilla_save = Cuadrilla.objects.create(nombre_cuadrilla=nombre_cuadrilla, state=state)

            for cuadrilla_id in cuadrillas_ids:
                try:
                    usuario = User.objects.get(id=cuadrilla_id)

                    # Verificar si el usuario ya está en otra cuadrilla
                    if Miembro_cuadrilla.objects.filter(usuario=usuario).exists():
                        messages.warning(request, f'{usuario.first_name} {usuario.last_name} ya pertenece a otra cuadrilla.')
                        continue

                    # Crear relación miembro
                    Miembro_cuadrilla.objects.create(
                        cuadrilla=cuadrilla_save,
                        usuario=usuario,
                        cargo='Operario'  # por defecto
                    )

                except User.DoesNotExist:
                    continue

            messages.success(request, f'Cuadrilla "{nombre_cuadrilla}" creada con éxito.')
            return redirect('main_cuadrilla')

        else:
            messages.error(request, 'Método de solicitud no válido.')
            return redirect('main_cuadrilla')

    else:
        logout(request)
        return redirect('login')


@login_required
def asignar_jefe_cuadrilla(request, id_cuadrilla):
    cuadrilla = get_object_or_404(Cuadrilla, id_cuadrilla=id_cuadrilla)

    jefes_disponibles = Miembro_cuadrilla.objects.filter(cargo='Jefe de Cuadrilla', cuadrilla=cuadrilla)

    if request.method == 'POST':
        jefe_id = request.POST.get('jefe_id')
        if jefe_id:
            jefe = get_object_or_404(Miembro_cuadrilla, id=jefe_id)
            if jefe.cuadrilla != cuadrilla:
                messages.error(
                    request,
                    f'El usuario {jefe.usuario.get_full_name()} no pertenece a esta cuadrilla y no puede ser asignado como jefe.'
                )
            elif Cuadrilla.objects.filter(jefe_cuadrilla=jefe).exclude(id_cuadrilla=cuadrilla.id_cuadrilla).exists():
                messages.error(request,f'El jefe {jefe.usuario.get_full_name()} ya está asignado a otra cuadrilla.')
            else:
                cuadrilla.jefe_cuadrilla = jefe
                cuadrilla.save()
                messages.success(request, f'Se asignó a {jefe.usuario.get_full_name()} como jefe de la cuadrilla "{cuadrilla.nombre_cuadrilla}".')
                return redirect('main_cuadrilla')
        else:
            messages.error(request, 'Debe seleccionar un jefe válido.')

    return render(request, 'cuadrillas/asignar_jefe_cuadrilla.html', {
        'cuadrilla': cuadrilla,
        'jefes_disponibles': jefes_disponibles,
    })

@login_required
def asignar_departamento_cuadrilla(request, id_cuadrilla):
    cuadrilla = get_object_or_404(Cuadrilla, id_cuadrilla=id_cuadrilla)
    departamentos_disponibles = Departamento.objects.filter(state='Activo').order_by('nombre_dpto')

    if request.method == 'POST':
        departamento_id = request.POST.get('departamento_id')
        if departamento_id:
            departamento = get_object_or_404(Departamento, id=departamento_id)
            cuadrilla.departamento = departamento
            cuadrilla.save()
            messages.success(
                request,
                f'Se asignó el departamento "{departamento.nombre_dpto}" a la cuadrilla "{cuadrilla.nombre_cuadrilla}".'
            )
            return redirect('main_cuadrilla')
        else:
            messages.error(request, 'Debe seleccionar un departamento válido.')

    return render(request, 'cuadrillas/asignar_departamento_cuadrilla.html', {
        'cuadrilla': cuadrilla,
        'departamentos_disponibles': departamentos_disponibles,
    })

@login_required
def ver_cuadrillas(request, id_cuadrilla):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id ==  1: 
        try:
            cuadrilla_count = Cuadrilla.objects.filter(pk= id_cuadrilla).count()
            if cuadrilla_count <= 0: 
                messages.add_message(request,messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            cuadrilla_data= Cuadrilla.objects.get(pk=id_cuadrilla)
        except:
            messages.add_message(request,messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'cuadrillas/ver_cuadrillas.html'
        return render(request,template_name,{'cuadrilla_data':cuadrilla_data})
    else:
        logout(request)
        return redirect('login')

@login_required
def editar_cuadrillas(request, id_cuadrilla=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id != 1: 
        logout(request)
        return redirect('login')
    
    try:
        cuadrilla = Cuadrilla.objects.get(pk=id_cuadrilla)
    except Cuadrilla.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Cuadrilla no encontrada')
        return redirect('main_cuadrilla')

    if request.method == 'POST':
        try:
            nombre_cuadrilla = request.POST.get('nombre_cuadrilla')
            state = request.POST.get('state')
            usuarios_ids = request.POST.getlist('usuarios')

            # Validaciones
            if not nombre_cuadrilla:
                messages.add_message(request, messages.INFO, 'El nombre de cuadrilla es requerido')
                return redirect('main_cuadrilla')

            # SOLO actualizar nombre, estado y usuarios
            Cuadrilla.objects.filter(pk=id_cuadrilla).update(
                nombre_cuadrilla=nombre_cuadrilla,
                state=(state == 'true')
            )

            # Actualizar relación ManyToMany (usuarios)
            if usuarios_ids:
                try:
                    usuarios_ids = [int(uid) for uid in usuarios_ids]
                    cuadrilla.usuarios.set(usuarios_ids)
                except ValueError:
                    messages.add_message(request, messages.INFO, 'IDs de usuarios no válidos')

            messages.add_message(request, messages.INFO, 'Cuadrilla actualizada correctamente')
            return redirect('main_cuadrilla')

        except Exception as e:
            messages.add_message(request, messages.INFO, f'Error al actualizar la cuadrilla: {str(e)}')
            return redirect('main_cuadrilla')

    # GET request - mostrar formulario
    template_name = 'cuadrillas/editar_cuadrillas.html'
    todos_usuarios = User.objects.filter(groups__id=5, is_active=True).order_by('first_name', 'last_name')
    
    return render(request, template_name, {
        'cuadrilla_data': cuadrilla,
        'todos_usuarios': todos_usuarios
    })

@login_required
def bloquear_cuadrilla(request, id_cuadrilla):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id == 1: 
            cuadrilla_count = Cuadrilla.objects.filter(pk=id_cuadrilla).count()
            if cuadrilla_count <=0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            Cuadrilla.objects.filter(pk=id_cuadrilla).update(state=False)
            messages.add_message(request,messages.INFO, 'cuadrilla bloqueada')
            return redirect('main_cuadrilla')
    else: 
        messages.add_message(request,messages.INFO, 'Hubo un error')
        logout(request)
        return redirect('login')

@login_required
def listar_cuadrillas_bloqueadas(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        cuadrillas_bloqueadas = Cuadrilla.objects.filter(state=False)
        template_name= 'cuadrillas/listar_cuadrillas_bloqueadas.html'
        return render(request,template_name, {'cuadrillas_bloqueadas': cuadrillas_bloqueadas})
    else:
        messages.add_message(request, messages.INFO, 'No tienes permisos')
        logout(request)
        return redirect('login')

@login_required
def desbloquear_cuadrilla(request, id_cuadrilla):
    Cuadrilla.objects.filter(pk=id_cuadrilla).update(state=True)
    messages.add_message(request, messages.INFO, 'Cuadrilla desbloqueada')
    return redirect('listar_cuadrillas_bloqueadas')

# TODO LO DE OPERARIO
@login_required
def main_operario(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('login')

    if profile.group_id == 1:
        operario_listado = Miembro_cuadrilla.objects.select_related('usuario', 'cuadrilla').filter(state= True, cuadrilla__state=True, usuario__groups__id=5).order_by('usuario__first_name', 'usuario__last_name')
#agregue en el filter el state=true que hace referencia a los operarios.        
        template_name = 'cuadrillas/main_operario.html'
        context = {
            'operario_listado': operario_listado
        }
        return render(request, template_name, context)
    else:
        logout(request)
        return redirect('login')

@login_required
def cambiar_cargo(request, miembro_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error al obtener el perfil del usuario.')
        logout(request)
        return redirect('login')

    # Solo administradores pueden hacer esto (ajusta según tus permisos)
    if profile.group_id != 1:
        logout(request)
        return redirect('login')

    try:
        miembro = Miembro_cuadrilla.objects.select_related('usuario').get(id=miembro_id)
    except Miembro_cuadrilla.DoesNotExist:
        messages.error(request, 'No se encontró al miembro indicado.')
        return redirect('main_operario')

    # Si es jefe de cuadrilla, verificar si está asignado a alguna cuadrilla
    if miembro.cargo == 'Jefe de Cuadrilla':
        cuadrilla_asignada = Cuadrilla.objects.filter(jefe_cuadrilla=miembro).first()
        if cuadrilla_asignada:
            messages.error(
                request,
                f'No se puede cambiar el cargo de {miembro.usuario.get_full_name()} '
                f'mientras sea jefe de la cuadrilla "{cuadrilla_asignada.nombre_cuadrilla}". '
                f'Primero asigne otro jefe a esa cuadrilla.'
            )
            return redirect('main_operario')

    # Alternar el cargo
    if miembro.cargo == 'Operario':
        miembro.cargo = 'Jefe de Cuadrilla'
        mensaje = f'{miembro.usuario.first_name} {miembro.usuario.last_name} ahora es Jefe de Cuadrilla.'
    elif miembro.cargo == 'Jefe de Cuadrilla':
        miembro.cargo = 'Operario'
        mensaje = f'{miembro.usuario.first_name} {miembro.usuario.last_name} ahora es Operario.'
    else:
        mensaje = f'El cargo de {miembro.usuario.get_full_name()} no puede cambiarse automáticamente.'

    miembro.save()
    messages.success(request, mensaje)
    return redirect('main_operario')

@login_required
def ver_operario(request, usuario_id):
    try:
        profile = Profile.objects.filter(user_id = request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id ==  1: 
        try:
            operario_count = User.objects.filter(pk= usuario_id).count()
            if operario_count <= 0: 
                messages.add_message(request,messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            operario_data = User.objects.get(pk=usuario_id)
        except:
            messages.add_message(request,messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'cuadrillas/ver_operario.html'
        return render(request,template_name,{'operario_data':operario_data})
    else:
        logout(request)
        return redirect('login')
    
@login_required
def bloquear_operario(request, usuario_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id == 1: 
            operario_count = Miembro_cuadrilla.objects.filter(usuario_id=usuario_id).count()
            if operario_count <=0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            Miembro_cuadrilla.objects.filter(usuario_id=usuario_id).update(state=False)
            messages.add_message(request,messages.INFO, 'Operario bloqueado')
            return redirect('main_operario')  # ← CAMBIADO
    else: 
        messages.add_message(request,messages.INFO, 'Hubo un error')
        logout(request)
        return redirect('login')

@login_required
def listar_operarios_bloqueados(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        
        operarios_bloqueados = Miembro_cuadrilla.objects.filter(state=False)
        template_name= 'cuadrillas/listar_operarios_bloqueados.html'
        return render(request,template_name, {'operarios_bloqueados': operarios_bloqueados})
    else:
        messages.add_message(request, messages.INFO, 'No tienes permisos')
        logout(request)
        return redirect('login')
    
@login_required
def desbloquear_operario(request, usuario_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id == 1: 
        try:
            operario = Miembro_cuadrilla.objects.get(usuario_id=usuario_id)
            operario.state = True  
            operario.save()
            messages.add_message(request, messages.INFO, 'Operario desbloqueado')
            return redirect('listar_operarios_bloqueados')
        except Miembro_cuadrilla.DoesNotExist:
            messages.add_message(request, messages.INFO, 'Operario no encontrado')
            return redirect('listar_operarios_bloqueados')
    else:
        messages.add_message(request, messages.INFO, 'No tienes permisos')
        logout(request)
        return redirect('login')

#PERFIL CUADRILLA

def es_miembro_cuadrilla(user):
    return user.groups.filter(id=5).exists()

def filtrar_incidencias_cuadrilla(request, incidencias: QuerySet) -> QuerySet:
    estado_filtro = request.GET.get('estado', None)
    prioridad_filtro = request.GET.get('prioridad', None)

    if estado_filtro and estado_filtro in [e[0] for e in Incidencia.ESTADOS]:
        incidencias = incidencias.filter(estado=estado_filtro)

    if prioridad_filtro and prioridad_filtro in [p[0] for p in Incidencia.PRIORIDADES]:
        incidencias = incidencias.filter(prioridad=prioridad_filtro)

    return incidencias

def ordenar_incidencias_cuadrilla(request, incidencias: QuerySet) -> QuerySet:
    orden = request.GET.get('ordenar', 'prioridad')
    if orden == 'antiguas':
        return incidencias.order_by('fecha_creacion')
    if orden == 'recientes':
        return incidencias.order_by('-fecha_creacion')
    return incidencias.order_by('prioridad')

@login_required
@user_passes_test(es_miembro_cuadrilla, login_url='/accounts/login/')
def dashboard_cuadrilla(request):
    try:
        miembro = Miembro_cuadrilla.objects.get(usuario=request.user)
        cuadrilla_usuario = miembro.cuadrilla

        if miembro.cargo != "Jefe de Cuadrilla" or cuadrilla_usuario.jefe_cuadrilla != miembro:
            messages.error(request, 'Solo el jefe de cuadrilla puede acceder.')
            logout(request)
            return redirect('login')

    except Miembro_cuadrilla.DoesNotExist:
        messages.error(request, 'Usted no está asignado a ninguna cuadrilla.')
        return redirect('main_usuario')

    incidencias_listado = Incidencia.objects.filter(id_cuadrilla=cuadrilla_usuario)
    incidencias_listado = filtrar_incidencias_cuadrilla(request, incidencias_listado)
    incidencias_listado = ordenar_incidencias_cuadrilla(request, incidencias_listado)

    # 🔹 Bloqueo de iniciar proceso si hay incidencias activas o finalizadas sin cerrar
    hay_activa = Incidencia.objects.filter(
        id_cuadrilla=cuadrilla_usuario,
        estado__in=['proceso', 'finalizada']
    ).exists()

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
        'prioridades': Incidencia.PRIORIDADES,
        'estado_seleccionado': request.GET.get('estado', ''),
        'prioridad_seleccionada': request.GET.get('prioridad', ''),
        'orden_seleccionado': request.GET.get('ordenar', 'prioridad'),
        'cuadrilla_usuario': cuadrilla_usuario,
        'hay_activa': hay_activa,
    }
    return render(request, 'cuadrillas/dashboard_cuadrilla.html', context)

@login_required
@user_passes_test(es_miembro_cuadrilla, login_url='/accounts/login/')
def ver_incidencia_cuadrilla(request, id):
    try:
        miembro = Miembro_cuadrilla.objects.get(usuario=request.user)
        id_cuadrilla_usuario = miembro.cuadrilla.id_cuadrilla
    except Miembro_cuadrilla.DoesNotExist:
        messages.error(request, 'No tiene cuadrilla asignada.')
        return redirect('dashboard_cuadrilla')

    incidencia = get_object_or_404(
        Incidencia,
        id_incidencia=id,
        id_cuadrilla_id=id_cuadrilla_usuario
    )

    datos_vecino = get_object_or_404(DatosVecino, id_incidencia=incidencia)
    archivos = ArchivosMultimedia.objects.filter(id_incidencia=incidencia)
    respuestas = RegistrosRespuestas.objects.filter(id_incidencia=incidencia)
    evidencias = Registro_cierre.objects.filter(incidencia=incidencia)  

    return render(request, 'cuadrillas/ver_incidencia_cuadrilla.html', {
        'incidencia': incidencia,
        'datos_vecino': datos_vecino,
        'archivos': archivos,
        'respuestas': respuestas,
        'evidencias': evidencias,  
    })

@login_required
@user_passes_test(es_miembro_cuadrilla, login_url='/accounts/login/')
def subir_evidencia_cierre(request, id_incidencia):
    try:
        miembro = Miembro_cuadrilla.objects.get(usuario=request.user)
    except Miembro_cuadrilla.DoesNotExist:
        messages.error(request, 'No tiene cuadrilla asignada.')
        return redirect('dashboard_cuadrilla')

    incidencia = get_object_or_404(
        Incidencia,
        id_incidencia=id_incidencia,
        id_cuadrilla=miembro.cuadrilla
    )

    # 🔹 Aquí agregamos la validación nueva:
    if incidencia.estado != 'proceso':
        messages.warning(request, 'Solo puede subir evidencia cuando la incidencia está en proceso.')
        return redirect('dashboard_cuadrilla')

    # 🔹 Mantén esta parte igual:
    if incidencia.estado == 'finalizada':
        messages.warning(request, 'Esta incidencia ya se encuentra finalizada.')
        return redirect('dashboard_cuadrilla')

    if request.method == 'POST':
        form = RegistroCierreForm(request.POST, request.FILES)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.incidencia = incidencia
            registro.cuadrilla = miembro.cuadrilla
            registro.save()
            incidencia.estado = 'finalizada'
            incidencia.save()
            
            messages.success(request, f'¡Evidencia subida! La incidencia {incidencia.id_incidencia} ha sido marcada como FINALIZADA.')
            return redirect('dashboard_cuadrilla')
        else:
            messages.error(request, 'Error al subir la evidencia. Revise el formulario.')
    else:
        form = RegistroCierreForm()

    context = {
        'form': form,
        'incidencia': incidencia
    }
    return render(request, 'cuadrillas/subir_evidencia.html', context)

@login_required
def activar_proceso_incidencia(request, id_incidencia):

    incidencia = get_object_or_404(Incidencia, id_incidencia=id_incidencia)

    cuadrilla = incidencia.id_cuadrilla
    if not cuadrilla:
        messages.error(request, "Esta incidencia no tiene cuadrilla asignada.")
        return redirect('dashboard_cuadrilla')

    en_proceso = Incidencia.objects.filter(id_cuadrilla=cuadrilla, estado='proceso').exists()
    if en_proceso:
        messages.warning(request, "Ya hay una incidencia en proceso. Debe cerrarla antes de iniciar otra.")
        return redirect('dashboard_cuadrilla')


    if incidencia.estado != 'derivada':
        messages.error(request, "Solo las incidencias derivadas pueden iniciarse.")
        return redirect('dashboard_cuadrilla')

    incidencia.estado = 'proceso'
    incidencia.save()

    messages.success(request, f"La incidencia #{incidencia.id_incidencia} ha sido marcada como 'En proceso'.")
    return redirect('dashboard_cuadrilla')