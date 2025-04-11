from django.db import models
from usuarios.models import DatosContacto, DatosPersonales
from negocio.models import DatosDomicilio, DatosFiscales

# Create your models here.

class Cliente(models.Model):
    datos_personales = models.OneToOneField(DatosPersonales, on_delete=models.CASCADE, null=True, blank=True)
    datos_contacto = models.OneToOneField(DatosContacto, on_delete=models.CASCADE, null=True, blank=True)
    datos_fiscales = models.OneToOneField(DatosFiscales, on_delete=models.CASCADE, null=True, blank=True)
    domicilios = models.ManyToManyField(DatosDomicilio, blank=True)

    
    def __str__(self):
        nombre = self.datos_personales.nombre if self.datos_personales else "Sin nombre"
        rfc = self.datos_fiscales.rfc if self.datos_fiscales else "Sin RFC"
        primer_domicilio = self.domicilios.first()
        domicilio = str(primer_domicilio) if primer_domicilio else "Sin domicilio"
        
        return f"{nombre}"
        
    @property
    def nombre(self):
        return self.datos_personales.nombre if self.datos_personales else "Sin nombre"
    @property
    def correo(self):
        return self.datos_personales.email if self.datos_personales else "Sin correo"
