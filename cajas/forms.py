from django import forms
from .models import Caja, CajaApertura
from usuarios.utils import es_administrador

class CajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ["clave", "nombre"]

class CajaAperturaForm(forms.ModelForm):
    class Meta:
        model = CajaApertura
        fields = ["caja", "monto_inicial"]
    
    def __init__(self, *args, **kwargs):
        caja = kwargs.pop("caja", None)
        super().__init__(*args, **kwargs)

        if caja:
            self.fields["caja"].initial = caja
            self.fields["caja"].widget = forms.HiddenInput()

    def clean_monto_inicial(self):
        monto = self.cleaned_data.get("monto_inicial")
        if monto < 0:
            raise forms.ValidationError("El monto inicial no puede ser negativo.")
        return monto
