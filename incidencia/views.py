from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Incidencia, DatosVecino, ArchivosMultimedia, RegistrosRespuestas
from encuesta.models import Encuesta, Preguntas

def es_territorial(user):
    return user.groups.filter(name='Territorial').exists() or user.groups.filter(id=5).exists()

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def main_territorial(request):
    return render(request, 'incidencia/main_territorial.html')

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def incidencia_list(request):
    incidencias = Incidencia.objects.filter(id_territorial=request.user)
    return render(request, 'incidencia/incidencia_list.html', {'incidencias': incidencias})

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def incidencia_create(request):
    encuestas = Encuesta.objects.filter(activo=True)
    
    if request.method == 'POST':
        try:
            # 1. Crear la incidencia
            incidencia = Incidencia(
                id_encuesta_id=request.POST['id_encuesta'],
                id_territorial=request.user,
                descripcion=request.POST['descripcion'],
                direccion=request.POST['direccion'],
                lateral=request.POST.get('lateral', ''),
                longitud=request.POST.get('longitud', ''),
                prioridad=request.POST['prioridad'],
                estado='abierta'
            )
            incidencia.save()
            
            # 2. Guardar datos del vecino
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
            
            # 3. Guardar respuestas a las preguntas
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
            
            # 4. Guardar archivos multimedia
            archivos = request.FILES.getlist('archivos_multimedia')
            for archivo in archivos:
                tipo = determinar_tipo_archivo(archivo.name)
                ArchivosMultimedia.objects.create(
                    id_incidencia=incidencia,
                    tipo_archivo=tipo,
                    archivo=archivo,
                    descripcion=request.POST.get('descripcion_archivo', '')
                )
            
            return redirect('incidencia_list')
            
        except Exception as e:
            return render(request, 'incidencia/incidencia_create.html', {
                'encuestas': encuestas,
                'error': f'Error al crear incidencia: {str(e)}'
            })
    
    return render(request, 'incidencia/incidencia_create.html', {
        'encuestas': encuestas
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
@user_passes_test(es_territorial, login_url='/accounts/login/')
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

@login_required
@user_passes_test(es_territorial, login_url='/accounts/login/')
def cambiar_estado_incidencia(request, id):
    incidencia = get_object_or_404(Incidencia, id_incidencia=id, id_territorial=request.user)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Incidencia.ESTADOS):
            incidencia.estado = nuevo_estado
            incidencia.save()
        
        return redirect('incidencia_list')
    
    return render(request, 'incidencia/cambiar_estado.html', {
        'incidencia': incidencia,
        'estados': Incidencia.ESTADOS
    })

def get_preguntas_encuesta(request):
    id_encuesta = request.GET.get('id_encuesta')
    preguntas = Preguntas.objects.filter(id_encuesta_id=id_encuesta)
    
    data = []
    for pregunta in preguntas:
        data.append({
            'id_preguntas': pregunta.id_preguntas,
            'pregunta': pregunta.pregunta
        })
    
    return JsonResponse(data, safe=False)