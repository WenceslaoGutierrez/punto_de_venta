from django.db import models
from usuarios.models import Usuario
from django.utils.timezone import now


# Create your models here.

class Caja(models.Model):
    ESTADOS_CAJA = (
        ("ABIERTA", "Abierta"),
        ("CERRADA", "Cerrada"),
    )
    clave = models.CharField(max_length=10, unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=255, blank=False, null=False)
    estado = models.CharField(max_length=10, choices=ESTADOS_CAJA, default="CERRADA")

    def __str__(self):
        return f"{self.clave} - {self.nombre}"
    
    def tiene_apertura_activa(self):
        return self.aperturas.filter(fecha_cierre__isnull=True).exists()

    def obtener_apertura_activa(self):
        return self.aperturas.filter(fecha_cierre__isnull=True).first()

    

class CajaApertura(models.Model):
    caja=models.ForeignKey(Caja, on_delete=models.CASCADE,related_name="aperturas")
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="cajas_abiertas")
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=False, null=False)
    monto_vendido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=False, null=False)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=False, null=False)
    fecha_apertura = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def usuario_tiene_caja_abierta(usuario):
        return CajaApertura.objects.filter(vendedor=usuario, caja__estado="ABIERTA").exists()

    @staticmethod
    def obtener_caja_abierta_usuario(usuario):
        return CajaApertura.objects.filter(vendedor=usuario, caja__estado="ABIERTA",fecha_cierre__isnull=True).first()

    def puede_cerrar(self, usuario):
        return usuario.rol == "ADMIN" or self.vendedor == usuario
    
    def validar_caja_abierta(self):
        if self.caja.estado == "CERRADA":
            raise ValueError("No se pueden realizar operaciones en una caja cerrada.")

    def cerrar_caja(self, usuario):
        self.validar_caja_abierta()

        if not self.puede_cerrar(usuario):
            raise ValueError("No tienes permiso para cerrar esta caja.")
        
        self.fecha_cierre = now()
        self.save()
        self.caja.estado = "CERRADA"
        self.caja.save()
    
    #Ajuste manual del monto vendido
    def actualizar_monto_vendido(self, monto_vendido):
        self.validar_caja_abierta()
        if monto_vendido < 0:
            raise ValueError("El monto vendido no puede ser negativo.")
        self.monto_vendido = monto_vendido
        self.monto_final = self.monto_inicial + monto_vendido
        self.save()
    
    #Incrementar monto vendido al hacer una venta
    def agregar_venta(self,monto_venta):
        self.validar_caja_abierta()
        if monto_venta < 0:
            raise ValueError("El monto de venta no puede ser negativo.")
        self.monto_vendido += monto_venta
        self.monto_final = self.monto_inicial + self.monto_vendido
        self.save()
    
    #Mostrar detalles de la caja
    def obtener_detalles(self):
        return{
            "monto_inicial": self.monto_inicial,
            "monto_vendido": self.monto_vendido,
            "monto_final": self.monto_final,
            "fecha_apertura": self.fecha_apertura,
            "fecha_cierre": self.fecha_cierre if self.fecha_cierre else "Aún abierta",
            "vendedor": self.vendedor.username,
            "estado": self.caja.estado,
        }
    
    def __str__(self):
        return f"Caja {self.caja.clave} {self.caja.nombre}  - {self.vendedor.username} - {self.caja.estado}"