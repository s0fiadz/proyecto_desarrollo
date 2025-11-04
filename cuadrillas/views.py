from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from registration.models import Profile, User
from cuadrillas.models import Cuadrilla, Miembro_cuadrilla
from departamento.models import Departamento

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
        template_name = 'cuadrillas/main_cuadrilla.html'
        return render(request, template_name,{'cuadrilla_listado': cuadrilla_listado})
    else:
        return redirect('logout')

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
        return redirect('logout')


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
        return redirect('logout')


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
        return redirect('logout')

@login_required
def editar_cuadrillas(request, id_cuadrilla=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id != 1: 
        return redirect('logout')
    
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
        return redirect('logout')

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
        return redirect('logout')

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
        return redirect('logout')

@login_required
def cambiar_cargo(request, miembro_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error al obtener el perfil del usuario.')
        return redirect('login')

    # Solo administradores pueden hacer esto (ajusta según tus permisos)
    if profile.group_id != 1:
        return redirect('logout')

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
        return redirect('logout')
    
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
        return redirect('logout')

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
        return redirect('logout')
    
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
        return redirect('logout')