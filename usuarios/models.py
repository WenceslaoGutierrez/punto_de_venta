from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings
# Create your models here.


class DatosPersonales(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class DatosContacto(models.Model):
    telefono = models.CharField(max_length=15, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    #url

    def __str__(self):
        return self.email if self.email else "Sin correo"

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('VENDEDOR', 'Vendedor'),
    )
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_usuario", null=True, blank=True)
    rol = models.CharField(max_length=10, choices=ROLES, default='VENDEDOR')
    datos_personales=models.OneToOneField(DatosPersonales, on_delete=models.CASCADE, null=True,blank=True)
    datos_contacto=models.OneToOneField(DatosContacto, on_delete=models.CASCADE, null=True,blank=True) 

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
            self.usuario = self
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.username} - {self.rol}"