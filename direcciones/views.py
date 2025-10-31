from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.shortcuts import redirect, render, get_object_or_404
from registration.models import Profile
from direcciones.models import Direccion, encargado_direccion
from django.contrib.auth.models import User



# Create your views here.

@login_required
def main_direccion(request):
    try: 
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('login')

    if profile.group_id == 1:
        direccion_listado = Direccion.objects.filter(state=True).order_by('nombre_direccion')
        template_name = 'direcciones/main_direccion.html'
        return render(request, template_name,{'direccion_listado': direccion_listado})
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
    
