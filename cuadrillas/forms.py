from django import forms
from .models import Registro_cierre

class RegistroCierreForm(forms.ModelForm):
    class Meta:
        model = Registro_cierre
        fields = ['descripcion', 'evidencia']
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'evidencia': forms.FileInput(attrs={'class': 'form-control', 'required': True}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descripcion'].label = "Descripción del Cierre (Opcional)"
        self.fields['evidencia'].label = "Archivo de Evidencia (Requerido)"