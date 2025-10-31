from django.shortcuts import render, redirect, get_object_or_404
from .models import Encuesta, TipoIncidencia, Preguntas

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
    encuestas = Encuesta.objects.all()
    return render(request, 'encuesta/encuesta_list.html', {'encuestas': encuestas})

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