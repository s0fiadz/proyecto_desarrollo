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
from .models import EncargadoDepartamento
from django.db.models.query import QuerySet

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
        return redirect('logout') 

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
        return redirect('logout') 
    
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
        return redirect('logout')

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
            return redirect('logout')

        template_name = 'departamento/editar_departamento.html'
        return render(request, template_name, {'departamento': departamento, 'direcciones': direcciones})
    else:
        return redirect('logout')
#Funcion ver_departamento
@login_required
def ver_departamento(request, id=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')

    if profile.group_id == 1:
        departamento = get_object_or_404(Departamento, pk=id)

        template_name = 'departamento/ver_departamento.html'
        return render(request, template_name, {'departamento': departamento})
    else:
        return redirect('logout')
    
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
        return redirect('logout')
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