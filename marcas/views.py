from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Marca
from .forms import MarcaForm
from usuarios.utils import solo_administrador

# Create your views here.

#CRUD
#Read
@login_required
@solo_administrador
def lista_marcas(request):
    query = request.GET.get("q", "").strip()

    marcas = Marca.objects.all()

    if query:
        marcas = marcas.filter(nombre__icontains=query)

    # Respuesta para AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "objetos": [
                {
                    "id": m.id,
                    "campos": [m.nombre],
                    "editar_url": reverse("editar_marca", args=[m.id]),
                    "eliminar_url": reverse("eliminar_marca", args=[m.id])
                }
                for m in marcas
            ],
            "es_admin": True,
            "encabezados": ["Nombre de Marca"]
        }
        return JsonResponse(data)

    # Definir los valores cuando no se usa AJAX
    for marca in marcas:
        marca.editar_url = reverse("editar_marca", args=[marca.id])
        marca.eliminar_url = reverse("eliminar_marca", args=[marca.id])

    contexto = {
        "titulo": "Marcas",
        "encabezados": ["Nombre de Marca"],
        "campos": ["nombre"],
        "texto_boton": "Marca",
        "objetos": marcas,
        "es_admin": True,
        "agregar_url": reverse("agregar_marca"),
    }

    return render(request, "crud/lista_base.html", contexto)

#Create
@login_required
@solo_administrador
def agregar_marca(request):
    if request.method == "POST":
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca agregada exitosamente.")
            return redirect("lista_marcas")
    else:
        form = MarcaForm()

    contexto = {
        "titulo": "Agregar Marca",
        "boton_texto": "Guardar Marca",
        "action_url": reverse("agregar_marca"),
        "formularios": [(form, "Datos de la Marca")],
        "volver_url": reverse("lista_marcas"),
    }

    return render(request, "crud/formulario_base.html", contexto)


#Update
@login_required
@solo_administrador
def editar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)

    if request.method == "POST":
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, "Marca actualizada exitosamente.")
            return redirect("lista_marcas")
    else:
        form = MarcaForm(instance=marca)

    contexto = {
        "titulo": "Editar Marca",
        "boton_texto": "Actualizar Marca",
        "action_url": reverse("editar_marca", args=[marca_id]),
        "formularios": [(form, "Datos de la Marca")],
        "volver_url": reverse("lista_marcas"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Delete
@login_required
@solo_administrador
def eliminar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)

    if request.method == "POST":
        marca.delete()
        messages.success(request, "Marca eliminada correctamente.")
        return redirect("lista_marcas")

    return redirect("lista_marcas")
