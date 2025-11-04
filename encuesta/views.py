from django.shortcuts import render, redirect, get_object_or_404
from .models import Encuesta, TipoIncidencia, Preguntas
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from incidencia.models import Incidencia
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def filtrar_encuestas(request, queryset):
    tipo_incidencia_id = request.GET.get('tipo_incidencia_id')
    estado = request.GET.get('estado')
    search_query = request.GET.get('search')

    # Filtrar por tipo de incidencia
    if tipo_incidencia_id and tipo_incidencia_id.isdigit():
        queryset = queryset.filter(id_tipo_incidencia_id=tipo_incidencia_id)

    # 🔹 Filtrar por estado (Activo/Inactivo)
    if estado in ['True', 'False']:
        queryset = queryset.filter(activo=(estado == 'True'))

    # Filtrar por búsqueda en título o descripción
    if search_query:
        queryset = queryset.filter(
            Q(titulo__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )

    return queryset


def ordenar_encuestas(request, queryset):
    orden = request.GET.get('ordenar')

    if orden == 'titulo_asc':
        return queryset.order_by('titulo')
    elif orden == 'titulo_desc':
        return queryset.order_by('-titulo')
    elif orden == 'tipo_incidencia':
        return queryset.order_by('id_tipo_incidencia__nombre')

    return queryset.order_by('-id_encuesta')

def encuesta_create(request):
    
    tipos_incidencia = TipoIncidencia.objects.all()
    
    if request.method == 'POST':
        try:
            # Datos de la encuesta
            titulo = request.POST['titulo']
            id_tipo_incidencia = request.POST['tipo_incidencia']
            descripcion = request.POST.get('descripcion', '')
            activo = 'activo' in request.POST
            
            # Verificar que haya al menos una pregunta
            preguntas_texto = request.POST.getlist('preguntas[]')
            if not any(pregunta.strip() for pregunta in preguntas_texto):
                return render(request, 'encuesta/encuesta_create.html', {
                    'tipos_incidencia': tipos_incidencia,
                    'error': 'Debe agregar al menos una pregunta'
                })
            
            # Crear la encuesta
            encuesta = Encuesta(
                titulo=titulo,
                descripcion=descripcion,
                id_tipo_incidencia_id=id_tipo_incidencia,
                activo=activo
            )
            encuesta.save()
            
            # Procesar las preguntas
            for texto_pregunta in preguntas_texto:
                if texto_pregunta.strip():  # Solo crear preguntas no vacías
                    Preguntas.objects.create(
                        id_encuesta=encuesta,
                        pregunta=texto_pregunta.strip()
                    )
            
            return redirect('encuesta_list')
            
        except Exception as e:
            return render(request, 'encuesta/encuesta_create.html', {
                'tipos_incidencia': tipos_incidencia,
                'error': f'Error al crear encuesta: {str(e)}'
            })
    
    return render(request, 'encuesta/encuesta_create.html', {
        'tipos_incidencia': tipos_incidencia
    })

def encuesta_view(request, id):
    encuesta = get_object_or_404(Encuesta, id_encuesta=id)
    preguntas = Preguntas.objects.filter(id_encuesta=encuesta)
    return render(request, 'encuesta/encuesta_view.html', {
        'encuesta': encuesta,
        'preguntas': preguntas
    })

def encuesta_edit(request, id):
    encuesta = get_object_or_404(Encuesta, id_encuesta=id)
    tipos_incidencia = TipoIncidencia.objects.all()
    preguntas = Preguntas.objects.filter(id_encuesta=encuesta)
    
    if request.method == 'POST':
        try:
            # Actualizar datos de la encuesta
            encuesta.titulo = request.POST.get('titulo')
            encuesta.descripcion = request.POST.get('descripcion')
            encuesta.id_tipo_incidencia_id = request.POST.get('tipo_incidencia')
            encuesta.activo = request.POST.get('activo') == 'on'
            encuesta.save()
            
            # Actualizar preguntas existentes
            preguntas_existentes = request.POST.getlist('preguntas_existentes[]')
            ids_preguntas = request.POST.getlist('ids_preguntas[]')
            
            for i, id_pregunta in enumerate(ids_preguntas):
                if id_pregunta:  # Pregunta existente
                    try:
                        pregunta = Preguntas.objects.get(id_preguntas=id_pregunta, id_encuesta=encuesta)
                        if i < len(preguntas_existentes) and preguntas_existentes[i].strip():
                            pregunta.pregunta = preguntas_existentes[i]
                            pregunta.save()
                    except Preguntas.DoesNotExist:
                        pass
            
            # Agregar nuevas preguntas
            nuevas_preguntas = request.POST.getlist('nuevas_preguntas[]')
            for texto_pregunta in nuevas_preguntas:
                if texto_pregunta.strip():
                    Preguntas.objects.create(
                        id_encuesta=encuesta,
                        pregunta=texto_pregunta.strip()
                    )
            
            return redirect('encuesta_list')
            
        except Exception as e:
            return render(request, 'encuesta/encuesta_edit.html', {
                'encuesta': encuesta,
                'tipos_incidencia': tipos_incidencia,
                'preguntas': preguntas,
                'error': f'Error al editar encuesta: {str(e)}'
            })
    
    return render(request, 'encuesta/encuesta_edit.html', {
        'encuesta': encuesta,
        'tipos_incidencia': tipos_incidencia,
        'preguntas': preguntas
    })

def encuesta_list(request):
    encuestas_list = Encuesta.objects.all().select_related('id_tipo_incidencia')

    encuestas_list = filtrar_encuestas(request, encuestas_list)
    encuestas_list = ordenar_encuestas(request, encuestas_list)

    page = request.GET.get('page', 1)
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10

    paginator = Paginator(encuestas_list, per_page)

    try:
        encuestas = paginator.page(page)
    except PageNotAnInteger:
        encuestas = paginator.page(1)
    except EmptyPage:
        encuestas = paginator.page(paginator.num_pages)

    todos_los_tipos = TipoIncidencia.objects.all()

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_params_str = query_params.urlencode()

    context = {
        'encuestas': encuestas,
        'todos_los_tipos': todos_los_tipos,
        'selected_tipo_id': request.GET.get('tipo_incidencia_id'),
        'selected_estado': request.GET.get('estado'),
        'selected_orden': request.GET.get('ordenar'),
        'search_query': request.GET.get('search'),
        'query_params': query_params_str,
    }

    return render(request, 'encuesta/encuesta_list.html', context)

def encuesta_toggle(request, id):
    encuesta = get_object_or_404(Encuesta, id_encuesta=id)
    encuesta.activo = not encuesta.activo
    encuesta.save()
    return redirect('encuesta_list')

def eliminar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(Preguntas, id_preguntas=id_pregunta)
    id_encuesta = pregunta.id_encuesta.id_encuesta
    pregunta.delete()
    return redirect('encuesta_edit', id=id_encuesta)