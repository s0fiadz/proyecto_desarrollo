from django.db import models
from django.contrib.auth.models import User

class Incidencia(models.Model):
    ESTADOS = [('abierta', 'Abierta'), ('derivada', 'Derivada'), ('rechazada', 'Rechazada'), 
                ('proceso', 'En Proceso'), ('finalizada', 'Finalizada'), ('cerrada', 'Cerrada')]
    
    PRIORIDADES = [('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')]
    
    id_incidencia = models.AutoField(primary_key=True)
    id_encuesta = models.ForeignKey('encuesta.Encuesta', on_delete=models.CASCADE, db_column='ID_encuesta')
    id_territorial = models.ForeignKey(User, on_delete=models.CASCADE, db_column='ID_territorial')
    id_direuntamiento = models.IntegerField(blank=True, null=True)
    id_caudrilla = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)
    lateral = models.CharField(max_length=100, blank=True, null=True)
    longitud = models.CharField(max_length=100, blank=True, null=True)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incidencia'
    
    def __str__(self):
        return f"Incidencia {self.id_incidencia} - {self.direccion}"

class DatosVecino(models.Model):
    id_vicino = models.AutoField(primary_key=True)
    id_incidencia = models.ForeignKey('incidencia.Incidencia', on_delete=models.CASCADE, db_column='ID_incidencia')
    id_encuesta = models.ForeignKey('encuesta.Encuesta', on_delete=models.CASCADE, db_column='ID_encuesta')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(blank=True, null=True)
    direccion_vicina = models.CharField(max_length=255)
    rat = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'datos_vecino'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class ArchivosMultimedia(models.Model):
    TIPOS_ARCHIVO = [('imagen', 'Imagen'), ('video', 'Video'), ('audio', 'Audio'), 
                     ('documento', 'Documento'), ('otro', 'Otro')]
    
    id_multimedia = models.AutoField(primary_key=True)
    id_incidencia = models.ForeignKey('incidencia.Incidencia', on_delete=models.CASCADE, db_column='ID_incidencia')
    tipo_archivo = models.CharField(max_length=20, choices=TIPOS_ARCHIVO)
    archivo = models.FileField(upload_to='incidencias/multimedia/')
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'archivos_multimedia'
    
    def __str__(self):
        return f"Archivo {self.id_multimedia} - {self.tipo_archivo}"

class RegistrosRespuestas(models.Model):
    id_reguerdas = models.AutoField(primary_key=True)
    id_preguntas = models.ForeignKey('encuesta.Preguntas', on_delete=models.CASCADE, db_column='ID_preguntas')
    id_incidencia = models.ForeignKey('incidencia.Incidencia', on_delete=models.CASCADE, db_column='ID_incidencia')
    respuesta = models.TextField()
    
    class Meta:
        db_table = 'registros_respuestas'
        unique_together = ['id_preguntas', 'id_incidencia']
    
    def __str__(self):
        return f"Respuesta {self.id_reguerdas}"