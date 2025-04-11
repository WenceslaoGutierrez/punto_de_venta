from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Departamento
from .forms import DepartamentoForm
from usuarios.utils import solo_administrador

# Create your views here.

#CRUD
#Read
@login_required
@solo_administrador
def lista_departamentos(request):
    query = request.GET.get("q", "").strip()

    departamentos = Departamento.objects.all()

    if query:
        departamentos = departamentos.filter(nombre__icontains=query)

    # Respuesta para AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "objetos": [
                {
                    "id": departamento.id,
                    "campos": [departamento.nombre],
                    "editar_url": reverse("editar_departamento", args=[departamento.id]),
                    "eliminar_url": reverse("eliminar_departamento", args=[departamento.id])
                }
                for departamento in departamentos
            ],
            "es_admin": True,
            "encabezados": ["Nombre de Departamento"]
        }
        return JsonResponse(data)

    # Definir los valores cuando no se usa AJAX
    for departamento in departamentos:
        departamento.editar_url = reverse("editar_departamento", args=[departamento.id])
        departamento.eliminar_url = reverse("eliminar_departamento", args=[departamento.id])

    contexto = {
        "titulo": "Departamentos",
        "encabezados": ["Nombre de Departamento"],
        "campos": ["nombre"],
        "texto_boton": "Departamento",
        "objetos": departamentos,
        "es_admin": True,
        "agregar_url": reverse("agregar_departamento"),
    }

    return render(request, "crud/lista_base.html", contexto)

#Create
@login_required
@solo_administrador
def agregar_departamento(request):
    if request.method == "POST":
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Departamento agregado exitosamente.")
            return redirect("lista_departamentos")
    else:
        form = DepartamentoForm()

    contexto = {
        "titulo": "Agregar Departamento",
        "boton_texto": "Guardar Departamento",
        "action_url": reverse("agregar_departamento"),
        "formularios": [(form, "Datos del Departamento")],
        "volver_url": reverse("lista_departamentos"),
    }

    return render(request, "crud/formulario_base.html", contexto)


#Update
@login_required
@solo_administrador
def editar_departamento(request, departamento_id):
    departamento = get_object_or_404(Departamento, id=departamento_id)

    if request.method == "POST":
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, "Departamento actualizado exitosamente.")
            return redirect("lista_departamentos")
    else:
        form = DepartamentoForm(instance=departamento)

    contexto = {
        "titulo": "Editar Departamento",
        "boton_texto": "Actualizar Departamento",
        "action_url": reverse("editar_departamento", args=[departamento_id]),
        "formularios": [(form, "Datos del Departamento")],
        "volver_url": reverse("lista_departamentos"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Delete
@login_required
@solo_administrador
def eliminar_departamento(request, departamento_id):
    departamento = get_object_or_404(Departamento, id=departamento_id)

    if request.method == "POST":
        departamento.delete()
        messages.success(request, "Departamento eliminado correctamente.")
        return redirect("lista_departamentos")

    return redirect("lista_departamentos")
