from django.db import models
from departamento.models import Departamento    
from django.contrib.auth.models import User

# Create your models here.

class  Cuadrilla(models.Model):
    id_cuadrilla = models.AutoField(primary_key=True)
    nombre_cuadrilla = models.CharField(max_length=100)
    jefe_cuadrilla = models.ForeignKey( 'Miembro_cuadrilla', on_delete=models.SET_NULL, null=True, blank=True, related_name='cuadrillas_dirigidas', limit_choices_to={'cargo': 'Jefe de Cuadrilla'}, unique=True)
    state = models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    departamento = models.ForeignKey(Departamento,on_delete=models.CASCADE,related_name='cuadrillas',null=True,blank=True,)
    usuarios = models.ManyToManyField(User, through = 'Miembro_cuadrilla', related_name='cuadrillas')

    class Meta:
        verbose_name = "Cuadrilla"
        verbose_name_plural = "Cuadrillas"
        ordering = ['nombre_cuadrilla']

    def __str__(self):
        return self.nombre_cuadrilla
    
class Miembro_cuadrilla(models.Model):
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE, db_column='id_cuadrilla')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_usuario')
    cargo = models.CharField(max_length=100, choices = [('Operario','Operario'),('Jefe de Cuadrilla','Jefe de Cuadrilla')], default='Operario')
    fecha_ingreso = models.DateField(auto_now_add=True)
    state = models.BooleanField(default=True)

    class Meta:
        unique_together = ('cuadrilla', 'usuario')
        verbose_name = "Miembro de Cuadrilla"
        verbose_name_plural = "Miembros de las Cuadrillas"
        ordering = ['cuadrilla__nombre_cuadrilla', 'usuario__first_name']

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - {self.cuadrilla.nombre_cuadrilla}"

class Registro_cierre(models.Model):
    id_registro = models.AutoField(primary_key=True)
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    evidencia = models.FileField(upload_to='cuadrillas/')
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE, db_column='id_cuadrilla', related_name='registros_de_cierre')
    incidencia = models.ForeignKey('incidencia.Incidencia', on_delete=models.CASCADE, db_column='id_incidencia', related_name='registros_cierre', null=True, blank=True)
    comentario_territorial = models.TextField(blank=True, null=True)
    state = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro de Cierre"
        verbose_name_plural = "Registros de Cierre"
        ordering = ['-fecha_cierre']

    def __str__(self):
        if self.incidencia:
            return f'Registro {self.id_registro} para Incidencia {self.incidencia.id_incidencia}'
        return f'Registro {self.id_registro} (sin incidencia asignada)'