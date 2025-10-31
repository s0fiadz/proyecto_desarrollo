from django import forms
from .models import EncuestaPlantilla, Encuesta

class EncuestaPlantillaForm(forms.ModelForm):
    class Meta:
        model = EncuestaPlantilla
        fields = ['titulo', 'descripcion', 'prioridad', 'tipo_incidencia']

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ['plantilla', 'vecino_nombre', 'vecino_celular', 'vecino_email']
