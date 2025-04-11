from django import forms
from .models import Unidad

class UnidadForm(forms.ModelForm):
    class Meta:
        model=Unidad
        exclude=[]