from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import json
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from clientes.models import Cliente
from cajas.models import Caja, CajaApertura
from productos.models import Producto
from usuarios.models import Usuario
from decimal import Decimal, InvalidOperation
from django.template.loader import get_template
from xhtml2pdf import pisa
from usuarios.utils import es_administrador
import pyexcel as pe

# Create your views here.

@login_required
def lista_ventas(request):
    query = request.GET.get("q", "").strip()
    filtro_caja = request.GET.get("caja")
    filtro_cliente = request.GET.get("cliente")
    filtro_vendedor = request.GET.get("vendedor")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    ventas = Venta.objects.select_related("cliente", "caja_apertura__caja", "caja_apertura__vendedor")
    
    filtros={}

    if query:
        ventas = ventas.filter(cliente__nombre__icontains=query)

    if filtro_caja:
        filtros["caja_apertura__caja__id"] = filtro_caja

    if filtro_cliente:
        filtros["cliente__id"] = filtro_cliente

    if es_administrador(request.user):
        if filtro_vendedor:
            filtros["caja_apertura__vendedor__id"] = filtro_vendedor
    else:
        filtros["caja_apertura__vendedor"] = request.user

    if fecha_inicio and fecha_fin:
        filtros["fecha__date__range"] = [fecha_inicio, fecha_fin]
    
    if filtros:
        ventas = ventas.filter(**filtros)


    # AJAX Response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        request.session["ventas_filtradas"] = list(ventas.values_list("id", flat=True))

        data = {
            "objetos": [
                {
                    "id": venta.id,
                    "campos": [
                        venta.id,
                        str(venta.caja_apertura.caja.nombre),
                        str(venta.cliente),
                        venta.caja_apertura.vendedor.username,
                        venta.fecha.strftime("%d/%m/%Y %H:%M"),
                        f"{venta.total:.2f}",
                    ],
                    "extra_acciones": (
                        f'<a href="{reverse("generar_ticket_pdf", args=[venta.id])}" target="_blank" class="btn btn-sm btn-primary">Ticket PDF</a>'
                    ),
                }
                for venta in ventas
            ],
            "encabezados": ["Folio", "Caja", "Cliente", "Vendedor", "Fecha", "Total"],
            "es_admin": es_administrador(request.user),
            "sin_edicion": True,
        }
        return JsonResponse(data)

    request.session["ventas_filtradas"] = list(ventas.values_list("id", flat=True))


    cajas = Caja.objects.all()
    clientes = Cliente.objects.all() 
    vendedores = Usuario.objects.all()

    contexto = {
        "titulo": "Ventas",
        "encabezados": ["Folio", "Caja", "Cliente", "Vendedor", "Fecha", "Total"],
        "campos": ["id", "caja", "cliente", "vendedor", "fecha_formateada", "total"],
        "texto_boton": "Venta",
        "objetos": ventas,
        "agregar_url": reverse("agregar_venta"),
        "es_admin": es_administrador(request.user),
        "sin_edicion": True,
        "cajas": cajas,
        "clientes": clientes,
        "vendedores": vendedores,
    }

    return render(request, "ventas/lista_ventas.html", contexto)

@login_required
def agregar_venta(request):
    apertura = CajaApertura.obtener_caja_abierta_usuario(request.user)

    contexto = {
            "mostrar_alerta": True,
            "titulo": "Agregar Venta"
    }

    if not apertura:
        return render(request, "ventas/agregar_venta.html", contexto)

    clientes = Cliente.objects.all()
    productos = Producto.objects.all()

    contexto= {
        "titulo": "Agregar Venta",
        "mostrar_alerta": False,
        "clientes": clientes,
        "productos": productos
    }

    return render(request, "ventas/agregar_venta.html", contexto)

@require_POST
@login_required
def crear_venta(request):
    try:
        data = json.loads(request.body)
        venta_data = data.get("venta")
        productos = data.get("productos", [])

        if not venta_data or not productos:
            return JsonResponse({"error": "Datos incompletos"}, status=400)

        cliente_id = venta_data.get("cliente_id")
        metodo_pago = venta_data.get("metodo_pago")
        
        importe = Decimal(str(venta_data.get("importe", 0)))
        cambio = Decimal(str(venta_data.get("cambio", 0)))
        descuento_general = Decimal(str(venta_data.get("descuento_general", 0)))

        cliente = Cliente.objects.get(pk=cliente_id)
        caja_abierta = CajaApertura.obtener_caja_abierta_usuario(request.user)

        # Calcular subtotal y total
        subtotal = Decimal("0.00")
        for p in productos:
            producto = Producto.objects.get(pk=p["id"])
            cantidad = int(p["cantidad"])
            descuento = Decimal(str(p.get("descuento", 0)))
            precio_unitario =Decimal(str( producto.precio))

            if cantidad > producto.stock:
                return JsonResponse({"error": f"No hay suficiente stock del producto {producto.nombre}. Stock disponible: {producto.stock}"}, status=400)
            
            subtotal += (precio_unitario * cantidad) * (Decimal("1") - descuento / Decimal("100"))

        total = subtotal * (Decimal("1") - descuento_general / Decimal("100"))

        # Crear la venta
        venta = Venta.objects.create(
            caja_apertura=caja_abierta,
            cliente=cliente,
            total=total,
            metodo_pago=metodo_pago,
            importe=importe,
            cambio=cambio,
            descuento_general=descuento_general
        )

        # Crear los detalles
        for p in productos:
            print("Producto recibido:", p)

            producto = Producto.objects.get(pk=p["id"])
            cantidad = int(p["cantidad"])
            descuento_raw = p.get("descuento", 0)
            descuento = Decimal(str(descuento_raw).strip())
            precio_unitario = producto.precio
            subtotal_detalle = (precio_unitario * cantidad) * (Decimal("1") - descuento / Decimal("100"))

            print("-> Creando detalle con:", {
                "producto": producto.nombre,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "descuento": descuento,
                "subtotal": subtotal_detalle
            })

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal_detalle,
                descuento=descuento
            )

            producto.stock-=cantidad
            producto.save()
        caja_abierta.refresh_from_db()
        caja_abierta.agregar_venta(total)
        return JsonResponse({"mensaje": "Venta registrada", "venta_id": venta.id})

    except (InvalidOperation, ValueError, KeyError) as e:
        return JsonResponse({"error": f"Error en datos numéricos: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def generar_ticket_pdf(request, venta_id):
    venta = get_object_or_404(Venta, pk=venta_id)

    if not es_administrador(request.user) and venta.caja_apertura.vendedor != request.user:
        messages.error(request, "No tienes permiso para ver este ticket.")
        return redirect("lista_ventas")

    detalles = venta.detalles.all()
    template_path = 'ventas/ticket_pdf.html'
    context = {'venta': venta,"detalles": detalles}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=ticket_venta_{venta.id}.pdf'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

@login_required
def exportar_ventas_excel(request):
    venta_ids = request.session.get("ventas_filtradas", [])

    if not venta_ids:
        return HttpResponse("No hay datos para exportar.", status=400)

    ventas = Venta.objects.filter(id__in=venta_ids).select_related(
        "cliente", "caja_apertura__caja", "caja_apertura__vendedor"
    ).prefetch_related("detalles__producto")

    filas = []
    for venta in ventas:
        filas.append([
            venta.id,
            venta.fecha.strftime("%d/%m/%Y %H:%M"),
            venta.cliente.nombre,
            venta.caja_apertura.vendedor.username,
            venta.caja_apertura.caja.nombre,
            float(venta.descuento_general),
            float(venta.total),
            venta.metodo_pago.capitalize(),
            float(venta.importe),
            float(venta.cambio)
        ])

    hoja = pe.Sheet([[
        "Folio", "Fecha", "Cliente", "Vendedor", "Caja", "Descuento General", 
        "Total Venta","Método de Pago", "Importe", "Cambio"
    ]] + filas)

    response = HttpResponse(
        hoja.xlsx,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=ventas_filtradas.xlsx"
    return response