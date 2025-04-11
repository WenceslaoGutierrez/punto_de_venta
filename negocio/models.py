from django.db import models
from usuarios.models import DatosContacto

# Create your models here.

class DatosDomicilio(models.Model):
    calle = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        direccion = ", ".join(filter(None, [self.calle, self.numero, self.colonia, self.ciudad, self.estado, self.codigo_postal]))
        return direccion if direccion else "Sin dirección"


class DatosFiscales(models.Model):
    rfc = models.CharField(max_length=13, unique=True, blank=True, null=True)
    razon_social = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.razon_social or 'Sin razón social'} ({self.rfc or 'Sin RFC'})"


class Negocio(models.Model):
    datos_fiscales = models.OneToOneField(DatosFiscales, on_delete=models.CASCADE, null=True, blank=True)
    datos_domicilio = models.OneToOneField(DatosDomicilio, on_delete=models.CASCADE, null=True, blank=True)
    datos_contacto= models.OneToOneField(DatosContacto, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.datos_fiscales or 'Sin datos fiscales'} | {self.datos_domicilio or 'Sin domicilio'} | {self.datos_contacto or 'Sin contacto'}"
