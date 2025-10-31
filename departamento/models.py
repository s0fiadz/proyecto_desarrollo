from django.db import models
from direcciones.models import Direccion
from django.contrib.auth.models import User


class Departamento(models.Model):
    nombre_dpto = models.CharField(max_length=100)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, null=True, blank=True)
    encargado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='departamentos_encargados')
    state = models.CharField(default='Activo', max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departamento'
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return self.nombre_dpto


class EncargadoDepartamento(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, db_column='id_departamento')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_usuario')

    class Meta:
        db_table = 'encargado_departamento'
        verbose_name = "Encargado de Departamento"
        verbose_name_plural = "Encargados de Departamentos"

    def __str__(self):
        return f"{self.usuario.username} - {self.departamento.nombre_dpto}"
