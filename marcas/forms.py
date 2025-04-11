from django import forms
from .models import Marca

class MarcaForm(forms.ModelForm):
    class Meta:
        model=Marca
        exclude=[]