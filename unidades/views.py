from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Unidad
from .forms import UnidadForm
from usuarios.utils import solo_administrador

# Create your views here.

#CRUD
#Read
@login_required
@solo_administrador
def lista_unidades(request):
    query = request.GET.get("q", "").strip()

    unidades = Unidad.objects.all()

    if query:
        unidades = unidades.filter(nombre__icontains=query)

    # Respuesta para AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "objetos": [
                {
                    "id": unidad.id,
                    "campos": [unidad.nombre],
                    "editar_url": reverse("editar_unidad", args=[unidad.id]),
                    "eliminar_url": reverse("eliminar_unidad", args=[unidad.id])
                }
                for unidad in unidades
            ],
            "es_admin": True,
            "encabezados": ["Nombre de Unidad"]
        }
        return JsonResponse(data)

    # Definir los valores cuando no se usa AJAX
    for unidad in unidades:
        unidad.editar_url = reverse("editar_unidad", args=[unidad.id])
        unidad.eliminar_url = reverse("eliminar_unidad", args=[unidad.id])

    contexto = {
        "titulo": "Unidades",
        "encabezados": ["Nombre de Unidad"],
        "campos": ["nombre"],
        "texto_boton": "Unidad",
        "objetos": unidades,
        "es_admin": True,
        "agregar_url": reverse("agregar_unidad"),
    }

    return render(request, "crud/lista_base.html", contexto)

#Create
@login_required
@solo_administrador
def agregar_unidad(request):
    if request.method == "POST":
        form = UnidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidad agregada exitosamente.")
            return redirect("lista_unidades")
    else:
        form = UnidadForm()

    contexto = {
        "titulo": "Agregar Unidad",
        "boton_texto": "Guardar Unidad",
        "action_url": reverse("agregar_unidad"),
        "formularios": [(form, "Datos de la unidad")],
        "volver_url": reverse("lista_unidades"),
    }

    return render(request, "crud/formulario_base.html", contexto)


#Update
@login_required
@solo_administrador
def editar_unidad(request, unidad_id):
    unidad = get_object_or_404(Unidad, id=unidad_id)

    if request.method == "POST":
        form = UnidadForm(request.POST, instance=unidad)
        if form.is_valid():
            form.save()
            messages.success(request, "Unidad actualizada exitosamente.")
            return redirect("lista_unidades")
    else:
        form = UnidadForm(instance=unidad)

    contexto = {
        "titulo": "Editar Unidad",
        "boton_texto": "Actualizar Unidad",
        "action_url": reverse("editar_unidad", args=[unidad_id]),
        "formularios": [(form, "Datos de la Unidad")],
        "volver_url": reverse("lista_unidades"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Delete
@login_required
@solo_administrador
def eliminar_unidad(request, unidad_id):
    unidad = get_object_or_404(Unidad, id=unidad_id)

    if request.method == "POST":
        unidad.delete()
        messages.success(request, "Unidad eliminada correctamente.")
        return redirect("lista_unidades")

    return redirect("lista_unidades")