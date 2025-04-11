from django import forms
from .models import Cliente
from negocio.models import DatosDomicilio, DatosFiscales
from usuarios.models import DatosContacto, DatosPersonales

class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        exclude = []

class DatosContactoForm(forms.ModelForm):
    class Meta:
        model = DatosContacto
        exclude = []

class DatosFiscalesForm(forms.ModelForm):
    class Meta:
        model = DatosFiscales
        exclude = []

class DatosDomicilioForm(forms.ModelForm):
    class Meta:
        model = DatosDomicilio
        exclude = []

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = []
