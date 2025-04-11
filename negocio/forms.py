from django import forms
from .models import Negocio, DatosFiscales, DatosDomicilio
from usuarios.models import DatosContacto  

class DatosDomicilioForm(forms.ModelForm):
    class Meta:
        model = DatosDomicilio
        exclude=[]

class DatosContactoForm(forms.ModelForm):
    class Meta:
        model = DatosContacto
        exclude=[]

class DatosFiscalesForm(forms.ModelForm):
    class Meta:
        model = DatosFiscales
        exclude=[]

class NegocioForm(forms.ModelForm):
    class Meta:
        model = Negocio
        fields = []