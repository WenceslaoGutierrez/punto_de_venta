from django.db import models
from cajas.models import CajaApertura
from usuarios.models import Usuario
from productos.models import Producto
from clientes.models import Cliente
from django.utils.timezone import now
from decimal import Decimal

# Create your models here.

class Venta(models.Model):
    caja_apertura = models.ForeignKey(CajaApertura, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, default="efectivo")
    importe = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    descuento_general = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=False)

    @property
    def caja(self):
        return self.caja_apertura.caja.nombre

    @property
    def vendedor(self):
        return self.caja_apertura.vendedor.username

    @property
    def fecha_formateada(self):
        return self.fecha.strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return f"Venta #{self.id} - ${self.total:.2f} - {self.caja_apertura.vendedor.username}"
    
    def puede_ver_ticket(self, usuario):
        return usuario.rol == "ADMIN" or self.caja_apertura.vendedor == usuario


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)


    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = (self.precio_unitario * self.cantidad) * (Decimal("1") - self.descuento / Decimal("100"))
        self.subtotal = self.subtotal.quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
