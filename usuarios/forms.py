from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import DatosPersonales, DatosContacto


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de Usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

User = get_user_model()
class UsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2", "rol"]

class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        exclude=[]

class DatosContactoForm(forms.ModelForm):
    class Meta:
        model = DatosContacto
        exclude=[]

class UsuarioEdicionForm(forms.ModelForm):
    nueva_contraseña = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Nueva contraseña",
        help_text="Deja este campo vacío si no deseas cambiar la contraseña."
    )

    class Meta:
        model = User
        fields = ["username", "rol"]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nueva_contraseña = self.cleaned_data.get("nueva_contraseña")
        if nueva_contraseña:
            usuario.set_password(nueva_contraseña)
        if commit:
            usuario.save()
        return usuario