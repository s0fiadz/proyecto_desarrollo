from django.db import models
from incidencia.models import Incidencia  # IMPORTAR desde la app incidencia

class TipoIncidencia(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'tipo_incidencia'
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
    
    def __str__(self):
        return self.nombre

class Encuesta(models.Model):
    id_encuesta = models.AutoField(primary_key=True)
    id_tipo_incidencia = models.ForeignKey(
        TipoIncidencia, 
        on_delete=models.CASCADE,
        db_column='ID_tipo_incidencia'
    )
    id_departamento = models.IntegerField(blank=True, null=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'encuesta'
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
    
    def __str__(self):
        return self.titulo

class Preguntas(models.Model):
    id_preguntas = models.AutoField(primary_key=True)
    id_encuesta = models.ForeignKey(
        Encuesta,
        on_delete=models.CASCADE,
        db_column='ID_encuesta',
        related_name='preguntas'
    )
    pregunta = models.TextField()
    
    class Meta:
        db_table = 'preguntas'
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
    
    def __str__(self):
        return f"{self.pregunta[:50]}..."


class Respuestas(models.Model):
    id_respuestas = models.AutoField(primary_key=True)
    id_preguntas = models.ForeignKey(
        Preguntas,
        on_delete=models.CASCADE,
        db_column='ID_preguntas'
    )
    id_incidencia = models.ForeignKey(
        Incidencia,  # AHORA viene de la app incidencia
        on_delete=models.CASCADE,
        db_column='ID_incidencia'
    )
    respuesta = models.TextField()
    
    class Meta:
        db_table = 'respuestas'
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        unique_together = ['id_preguntas', 'id_incidencia']
    
    def __str__(self):
        return f"Respuesta {self.id_respuestas}"