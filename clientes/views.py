from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from .models import Cliente
from .forms import ClienteForm, DatosPersonalesForm, DatosContactoForm, DatosFiscalesForm, DatosDomicilioForm
from negocio.models import DatosDomicilio, DatosFiscales
from usuarios.models import DatosContacto, DatosPersonales
from usuarios.utils import solo_administrador

# Create your views here.

# CRUD
#READ
@login_required
@solo_administrador
def lista_clientes(request):
    query = request.GET.get("q", "").strip()
    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(datos_personales__nombre__icontains=query)

    # AJAX - Respuesta en JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "objetos": [
                {
                    "id": c.id,
                    "campos": [
                        c.datos_personales.nombre if c.datos_personales else "Sin nombre",
                        c.datos_fiscales.rfc if c.datos_fiscales else "Sin RFC"
                    ],
                    "editar_url": reverse("editar_cliente", args=[c.id]),
                    "eliminar_url": reverse("eliminar_cliente", args=[c.id])
                }
                for c in clientes
            ],
            "es_admin": True,
            "encabezados": ["Nombre", "RFC"]
        }
        return JsonResponse(data)

    # Definir los valores cuando no se usa AJAX
    for cliente in clientes:
        cliente.fnombre = cliente.datos_personales.nombre if cliente.datos_personales else "Sin nombre"
        cliente.rfc = cliente.datos_fiscales.rfc if cliente.datos_fiscales else "Sin RFC"
        cliente.editar_url = reverse("editar_cliente", args=[cliente.id])
        cliente.eliminar_url = reverse("eliminar_cliente", args=[cliente.id])

    contexto = {
        "titulo": "Clientes",
        "encabezados": ["Nombre", "RFC"],
        "campos": ["fnombre", "rfc"],
        "texto_boton": "Cliente",
        "objetos": clientes,
        "agregar_url": reverse("agregar_cliente"),
        "es_admin": True,
    }

    return render(request, "crud/lista_base.html", contexto)

#CREATE
@login_required
@solo_administrador
def agregar_cliente(request):
    if request.method == "POST":
        datos_personales_form = DatosPersonalesForm(request.POST)
        datos_fiscales_form = DatosFiscalesForm(request.POST)
        datos_domicilio_form = DatosDomicilioForm(request.POST)
        datos_contacto_form = DatosContactoForm(request.POST)
        cliente_form = ClienteForm(request.POST)

        if datos_personales_form.is_valid():
            datos_personales = datos_personales_form.save()

            cliente = cliente_form.save(commit=False)
            cliente.datos_personales = datos_personales

            if datos_fiscales_form.is_valid() and any(datos_fiscales_form.cleaned_data.values()):
                datos_fiscales = datos_fiscales_form.save()
                cliente.datos_fiscales = datos_fiscales

            if datos_domicilio_form.is_valid() and any(datos_domicilio_form.cleaned_data.values()):
                datos_domicilio = datos_domicilio_form.save()
                cliente.datos_domicilio = datos_domicilio

            if datos_contacto_form.is_valid() and any(datos_contacto_form.cleaned_data.values()):
                datos_contacto = datos_contacto_form.save()
                cliente.datos_contacto = datos_contacto

            cliente.save()
            messages.success(request, "Cliente agregado exitosamente.")
            return redirect("lista_clientes")

    else:
        datos_personales_form = DatosPersonalesForm()
        datos_fiscales_form = DatosFiscalesForm()
        datos_domicilio_form = DatosDomicilioForm()
        datos_contacto_form = DatosContactoForm()
        cliente_form = ClienteForm()

    contexto = {
        "titulo": "Agregar Cliente",
        "boton_texto": "Guardar Cliente",
        "action_url": reverse("agregar_cliente"),
        "formularios": [
            (datos_personales_form, "Datos Personales"),
            (datos_fiscales_form, "Datos Fiscales"),
            (datos_domicilio_form, "Domicilio"),
            (datos_contacto_form, "Datos de Contacto"),
        ],
        "volver_url": reverse("lista_clientes"),
    }

    return render(request, "crud/formulario_base.html", contexto)

    
#UPDATE
@login_required
@solo_administrador
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    datos_personales = cliente.datos_personales if cliente.datos_personales else DatosPersonales()
    datos_contacto = cliente.datos_contacto if cliente.datos_contacto else DatosContacto()
    datos_fiscales = cliente.datos_fiscales if cliente.datos_fiscales else DatosFiscales()

    if request.method == "POST":
        datos_personales_form = DatosPersonalesForm(request.POST, instance=datos_personales)
        datos_contacto_form = DatosContactoForm(request.POST, instance=datos_contacto)
        datos_fiscales_form = DatosFiscalesForm(request.POST, instance=datos_fiscales)

        if datos_personales_form.is_valid() and datos_contacto_form.is_valid() and datos_fiscales_form.is_valid():
            datos_personales = datos_personales_form.save()
            datos_contacto = datos_contacto_form.save()
            datos_fiscales = datos_fiscales_form.save()

            cliente.datos_personales = datos_personales
            cliente.datos_contacto = datos_contacto
            cliente.datos_fiscales = datos_fiscales
            cliente.save()

            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("lista_clientes")
        else:
            messages.error(request, "Error al actualizar el cliente. Revisa los datos.")

    else:
        datos_personales_form = DatosPersonalesForm(instance=datos_personales)
        datos_contacto_form = DatosContactoForm(instance=datos_contacto)
        datos_fiscales_form = DatosFiscalesForm(instance=datos_fiscales)

    contexto = {
        "titulo": "Editar Cliente",
        "formularios": [
            (datos_personales_form, "Datos Personales"),
            (datos_contacto_form, "Datos de Contacto"),
            (datos_fiscales_form, "Datos Fiscales"),
        ],
        "boton_texto": "Guardar Cambios",
        "action_url": reverse("editar_cliente", args=[cliente.id]),
        "volver_url": reverse("lista_clientes")
    }

    return render(request, "crud/formulario_base.html", contexto)
    
#DELETE
@login_required
@solo_administrador
def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
        return redirect("lista_clientes")

    return redirect("lista_clientes")
