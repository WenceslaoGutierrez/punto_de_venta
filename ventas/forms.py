from django import forms
from ventas.models import Venta, DetalleVenta
from clientes.models import Cliente
from cajas.models import CajaApertura
from productos.models import Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['caja_apertura', 'cliente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['caja_apertura'].queryset = CajaApertura.objects.filter(caja__estado="ABIERTA")
        self.fields['cliente'].queryset = Cliente.objects.all()

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()