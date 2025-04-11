from ventas.models import Venta, DetalleVenta
from cajas.models import CajaApertura, Caja
from usuarios.models import Usuario
from productos.models import Producto
from clientes.models import Cliente
from datetime import date, time
from django.db.models import Count, Sum, F, Q, Value, Avg, Max, Min, DecimalField, ExpressionWrapper
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db import connection

def ejemplo_filter():
    filter_diccionario = {
        # TEXT LOOKUPS
        'contains': Producto.objects.filter(marca__nombre__contains='sabritas'),
        # sensible a mayusculas
        'icontains': Producto.objects.filter(nombre__icontains='doritos'),

        'startswith': Producto.objects.filter(nombre__startswith='dor'),
        'istartswith': Producto.objects.filter(nombre__istartswith='Dor'),
        
        'endswith': Producto.objects.filter(nombre__endswith='Tos'),
        'iendswith': Producto.objects.filter(nombre__iendswith='tos'),

        'exact': Producto.objects.filter(marca__nombre__exact='SABRITAS'),
        'iexact': Producto.objects.filter(marca__nombre__iexact='Sabritas'),

        'in': Producto.objects.filter(id__in=[1, 2, 3]),
        'regex': Producto.objects.filter(nombre__regex=r'^d[a-z]+'),
        'iregex': Producto.objects.filter(nombre__iregex=r'^D[a-z]+'),

        # NULL LOOKUP
        'isnull': Cliente.objects.filter(datos_contacto__email__isnull=True),

        # NUMERIC LOOKUPS
        'gt': Producto.objects.filter(precio__gt=65),
        'gte': Producto.objects.filter(precio__gte=69),
        'lt': Producto.objects.filter(precio__lt=20),
        'lte': Producto.objects.filter(precio__lte=20),
        'range': Producto.objects.filter(stock__range=(50, 55)),

        # DATE/TIME LOOKUPS
        'date': Venta.objects.filter(fecha__date=date(2025, 3, 28)),
        'day': Venta.objects.filter(fecha__day=27),
        'month': Venta.objects.filter(fecha__month=3),
        'year': Venta.objects.filter(fecha__year=2025),

        'quarter': Venta.objects.filter(fecha__quarter=1),
        'hour': Venta.objects.filter(fecha__hour=18),
        'minute': Venta.objects.filter(fecha__minute=29),
        'second': Venta.objects.filter(fecha__second=0),
        'time': Venta.objects.filter(fecha__time=time(22, 24)),
        
        'week': Venta.objects.filter(fecha__week=14),
        'week_day': Venta.objects.filter(fecha__week_day=5),         # Domingo=1
        'iso_week_day': Venta.objects.filter(fecha__iso_week_day=6), # Lunes=1
        'iso_year': Venta.objects.filter(fecha__iso_year=2025),

        # COMPLEJOS CON Q
        'or_logico': Producto.objects.filter(
            # filtrar marca sabritas o donde stock sea superior que 50
            Q(marca__nombre__icontains='Sabritas') | Q(stock__gt=50)
        ),

        'and_logico': Cliente.objects.filter(
            Q(datos_personales__nombre__contains='wences') & Q(datos_contacto__email__isnull=False)
        ),

        'not_logico': Producto.objects.filter(
            ~Q(stock__lt=10)
        ),
    }

    return filter_diccionario

def ejemplo_exclude():
    exclude_diccionario = {
        # TEXT LOOKUPS
        'contains': Producto.objects.exclude(marca__nombre__contains='sabritas'),
        # sensible a mayusculas
        'icontains': Producto.objects.exclude(nombre__icontains='doritos'),

        'startswith': Producto.objects.exclude(nombre__startswith='dor'),
        'istartswith': Producto.objects.exclude(nombre__istartswith='Dor'),
        
        'endswith': Producto.objects.exclude(nombre__endswith='Tos'),
        'iendswith': Producto.objects.exclude(nombre__iendswith='tos'),

        'exact': Producto.objects.exclude(marca__nombre__exact='SABRITAS'),
        'iexact': Producto.objects.exclude(marca__nombre__iexact='Sabritas'),

        'in': Producto.objects.exclude(id__in=[1, 2, 3]),
        'regex': Producto.objects.exclude(nombre__regex=r'^d[a-z]+'),
        'iregex': Producto.objects.exclude(nombre__iregex=r'^D[a-z]+'),

        # NULL LOOKUP
        'isnull': Cliente.objects.exclude(datos_contacto__email__isnull=True),

        # NUMERIC LOOKUPS
        'gt': Producto.objects.exclude(precio__gt=65),
        'gte': Producto.objects.exclude(precio__gte=69),
        'lt': Producto.objects.exclude(precio__lt=20),
        'lte': Producto.objects.exclude(precio__lte=20),
        'range': Producto.objects.exclude(stock__range=(50, 55)),

        # DATE/TIME LOOKUPS
        'date': Venta.objects.exclude(fecha__date=date(2025, 3, 28)),
        'day': Venta.objects.exclude(fecha__day=27),
        'month': Venta.objects.exclude(fecha__month=3),
        'year': Venta.objects.exclude(fecha__year=2025),

        'quarter': Venta.objects.exclude(fecha__quarter=1),
        'hour': Venta.objects.exclude(fecha__hour=18),
        'minute': Venta.objects.exclude(fecha__minute=29),
        'second': Venta.objects.exclude(fecha__second=0),
        'time': Venta.objects.exclude(fecha__time=time(22, 24)),
        
        'week': Venta.objects.exclude(fecha__week=14),
        'week_day': Venta.objects.exclude(fecha__week_day=5),         # Domingo=1
        'iso_week_day': Venta.objects.exclude(fecha__iso_week_day=6), # Lunes=1
        'iso_year': Venta.objects.exclude(fecha__iso_year=2025),

        # COMPLEJOS CON Q
        'or_logico': Producto.objects.exclude(
            # filtrar marca sabritas o donde stock sea superior que 50
            Q(marca__nombre__icontains='Sabritas') | Q(stock__gt=50)
        ),

        'and_logico': Cliente.objects.exclude(
            Q(datos_personales__nombre__contains='wences') & Q(datos_contacto__email__isnull=False)
        ),

        'not_logico': Producto.objects.exclude(
            ~Q(stock__lt=10)
        ),
    }

    return exclude_diccionario

def ejemplo_annotate():
    resultados = {
        # cantidad de productos en cada venta
        'productos_por_venta': Venta.objects.annotate(total_productos=Count('detalles')).values('id', 'total_productos'),

        # cantidad total vendida por producto
        'cantidad_total_vendida': Producto.objects.annotate(total_vendida=Coalesce(Sum('detalleventa__cantidad'), 0)).values('nombre', 'total_vendida'),

        # ingreso total generado por cada producto (precio_unitario * cantidad)
        'ingreso_total_por_producto': Producto.objects.annotate(ingreso=Coalesce(Sum(ExpressionWrapper(F('detalleventa__cantidad') * F('detalleventa__precio_unitario'),output_field=DecimalField(max_digits=10, decimal_places=2)),output_field=DecimalField(max_digits=10, decimal_places=2)),Decimal('0.00'))).values('nombre', 'ingreso'),

        # total de ventas realizadas por cliente
        'total_por_cliente': Cliente.objects.annotate(total=Coalesce(Sum('venta__total', output_field=DecimalField(max_digits=10, decimal_places=2)),Decimal('0.00'))).values('id', 'datos_personales__nombre', 'total'),

        # promedio de productos por venta
        'promedio_productos_por_venta': Venta.objects.annotate(promedio=Avg('detalles__cantidad')).values('id', 'promedio'),

        # maximo de productos vendidos en un solo detalle de una venta
        'maximo_productos_en_detalle': Venta.objects.annotate(maximo=Max('detalles__cantidad')).values('id', 'maximo'),

        # total recalculado a partir de los detalles
        'total_recalculado': Venta.objects.annotate(total_recalculado=Coalesce(Sum(ExpressionWrapper(F('detalles__cantidad') * F('detalles__precio_unitario'),output_field=DecimalField(max_digits=10, decimal_places=2)),output_field=DecimalField(max_digits=10, decimal_places=2)),Decimal('0.00'))).values('id', 'total', 'total_recalculado'),
    }

    return resultados
