from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Producto
from .forms import ProductoForm
from departamentos.models import Departamento
from unidades.models import Unidad
from marcas.models import Marca
from usuarios.utils import es_administrador, solo_administrador

# Create your views here.

#CRUD
#Read
@login_required
@solo_administrador
def lista_productos(request):
    query = request.GET.get("q", "").strip()
    marca_id = request.GET.get("marca", "").strip()
    departamento_id = request.GET.get("departamento", "").strip()
    unidad_id = request.GET.get("unidad", "").strip()
    stock_filtro = request.GET.get("stock", "").strip()
    ordenar_stock = request.GET.get("orden_stock", "").strip()

    productos = Producto.objects.all()

    es_admin = es_administrador(request.user)

    if query:
        productos = productos.filter(nombre__icontains=query)

    if marca_id:
        productos = productos.filter(marca_id=marca_id)

    if departamento_id:
        productos = productos.filter(departamento_id=departamento_id)

    if unidad_id:
        productos = productos.filter(unidad_id=unidad_id)

    if stock_filtro:
        if stock_filtro == "disponible":
            productos = productos.filter(stock__gt=0)
        elif stock_filtro == "sin_stock":
            productos = productos.filter(stock=0)

    if ordenar_stock:
        if ordenar_stock == "asc":
            productos = productos.order_by("stock")
        elif ordenar_stock == "desc":
            productos = productos.order_by("-stock")

    # AJAX Response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "objetos": [
                {
                    "id": producto.id,
                    "campos": [
                        producto.nombre,
                        producto.marca.nombre if producto.marca else "Sin marca asignada",
                        producto.departamento.nombre if producto.departamento else "Sin departamento asignado",
                        producto.unidad.nombre if producto.unidad else "Sin unidad asignada",
                        producto.precio,
                        producto.stock if producto.stock > 0 else "Sin stock",
                    ],
                    "editar_url": reverse("editar_producto", args=[producto.id]),
                    "eliminar_url": reverse("eliminar_producto", args=[producto.id]),
                }
                for producto in productos
            ],
            "es_admin": True,
            "encabezados": ["Nombre", "Marca", "Departamento", "Unidad", "Precio", "Stock"],
        }
        return JsonResponse(data)
    
    
    for producto in productos:
        producto.editar_url = reverse("editar_producto", args=[producto.id]) if es_admin else None
        producto.eliminar_url = reverse("eliminar_producto", args=[producto.id]) if es_admin else None

    contexto = {
        "titulo": "Productos",
        "encabezados": ["Nombre", "Marca", "Departamento", "Unidad", "Precio", "Stock"],
        "campos": ["nombre", "marca", "departamento", "unidad", "precio", "stock"],
        "texto_boton": "Producto",
        "objetos": productos,
        "es_admin": True,
        "agregar_url": reverse("agregar_producto"),
        "agregar_url": reverse("agregar_producto"),
        "marcas": Marca.objects.all(),
        "departamentos": Departamento.objects.all(),
        "unidades": Unidad.objects.all(),
    }

    return render(request, "productos/lista_productos.html", contexto)

#Create
@login_required
@solo_administrador
def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado exitosamente.")
            return redirect("lista_productos")
    else:
        form = ProductoForm()

    contexto = {
        "titulo": "Agregar Producto",
        "boton_texto": "Guardar Producto",
        "action_url": reverse("agregar_producto"),
        "formularios": [(form, "Datos del Producto")],
        "volver_url": reverse("lista_productos"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Update
@login_required
@solo_administrador
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado exitosamente.")
            return redirect("lista_productos")
    else:
        form = ProductoForm(instance=producto)

    contexto = {
        "titulo": "Editar Producto",
        "boton_texto": "Actualizar Producto",
        "action_url": reverse("editar_producto", args=[producto_id]),
        "formularios": [(form, "Datos del Producto")],
        "volver_url": reverse("lista_productos"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Remove
@login_required
@solo_administrador
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect("lista_productos")

    return redirect("lista_productos")