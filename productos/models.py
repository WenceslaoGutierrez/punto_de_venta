from django.db import models
from departamentos.models import Departamento
from unidades.models import Unidad
from marcas.models import Marca

# Create your models here.

class Producto(models.Model):
    nombre = models.CharField(max_length=255, unique=True, blank=False, null=False)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, null=True,blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True,blank=True)
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, null=True,blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False,blank=False)
    stock = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        marca = self.marca.nombre if self.marca else "Sin marca asignada"
        departamento = self.departamento.nombre if self.departamento else "Sin departamento asignado"
        unidad = self.unidad.nombre if self.unidad else "Sin unidad asignada"
        stock = self.stock if self.stock > 0 else "Sin stock"
        return f"{self.nombre} | {marca} | {departamento} | {unidad} | {stock} "