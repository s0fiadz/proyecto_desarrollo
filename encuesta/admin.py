from django.contrib import admin
from .models import TipoIncidencia, Encuesta, Preguntas, Respuestas
# ELIMINAR Incidencia del import

@admin.register(TipoIncidencia)
class TipoIncidenciaAdmin(admin.ModelAdmin):
    list_display = ('id_tipo', 'nombre')
    search_fields = ('nombre',)

class PreguntasInline(admin.TabularInline):
    model = Preguntas
    extra = 1

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('id_encuesta', 'titulo', 'id_tipo_incidencia')
    list_filter = ('id_tipo_incidencia',)
    search_fields = ('titulo', 'descripcion')
    inlines = [PreguntasInline]

@admin.register(Preguntas)
class PreguntasAdmin(admin.ModelAdmin):
    list_display = ('id_preguntas', 'pregunta_corta', 'id_encuesta')
    list_filter = ('id_encuesta',)
    search_fields = ('pregunta',)
    
    def pregunta_corta(self, obj):
        return obj.pregunta[:50] + '...' if len(obj.pregunta) > 50 else obj.pregunta
    pregunta_corta.short_description = 'Pregunta'

# ELIMINAR RespuestasInline y IncidenciaAdmin completamente
# class RespuestasInline(admin.TabularInline):
#     model = Respuestas
#     extra = 1

# @admin.register(Incidencia)
# class IncidenciaAdmin(admin.ModelAdmin):
#     list_display = ('id_incidencia', 'titulo', 'id_tipo_incidencia', 'fecha_creacion')
#     list_filter = ('id_tipo_incidencia', 'fecha_creacion')
#     search_fields = ('titulo', 'descripcion')
#     inlines = [RespuestasInline]

@admin.register(Respuestas)
class RespuestasAdmin(admin.ModelAdmin):
    list_display = ('id_respuestas', 'id_preguntas', 'id_incidencia', 'respuesta_corta')
    list_filter = ('id_incidencia', 'id_preguntas')
    
    def respuesta_corta(self, obj):
        return obj.respuesta[:50] + '...' if len(obj.respuesta) > 50 else obj.respuesta
    respuesta_corta.short_description = 'Respuesta'