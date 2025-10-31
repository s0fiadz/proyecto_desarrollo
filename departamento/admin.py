from django.contrib import admin
from .models import Departamento, EncargadoDepartamento


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre_dpto', 'direccion', 'state', 'created', 'updated')


@admin.register(EncargadoDepartamento)
class EncargadoDepartamentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'departamento')
