from django.db import models
from django.contrib.auth.models import User

# Create your models here.11

class Direccion(models.Model):
    id_direccion = models.AutoField(primary_key=True)
    nombre_direccion = models.CharField(max_length=100)
    state = models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['nombre_direccion']

    def __str__(self):
        return self.nombre_direccion

class encargado_direccion(models.Model):
    id_encargado = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, db_column='id_usuario')
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, db_column='id_direccion', related_name='encargado')

    class Meta:
        verbose_name = "Encargado de Direccion"
        verbose_name_plural = "Encargados de Direcciones"
        ordering = ['usuario']

    def __str__(self):
        return f'{self.usuario.first_name} {self.usuario.last_name}'
