from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Negocio, DatosDomicilio, DatosFiscales
from usuarios.models import DatosContacto
from .forms import NegocioForm, DatosDomicilioForm, DatosContactoForm, DatosFiscalesForm
from usuarios.utils import solo_administrador

# Create your views here.

@login_required
@solo_administrador
@login_required
def editar_negocio(request):
    negocio, created = Negocio.objects.get_or_create(id=1)
    if not negocio.datos_fiscales:
        datos_fiscales, _ = DatosFiscales.objects.get_or_create(rfc="", razon_social="")
        negocio.datos_fiscales = datos_fiscales

    if not negocio.datos_domicilio:
        datos_domicilio, _ = DatosDomicilio.objects.get_or_create()
        negocio.datos_domicilio = datos_domicilio

    if not negocio.datos_contacto:
        datos_contacto, _ = DatosContacto.objects.get_or_create()
        negocio.datos_contacto = datos_contacto

    negocio.save()

    if request.method == "POST":
        negocio_form = NegocioForm(request.POST, instance=negocio)
        datos_fiscales_form = DatosFiscalesForm(request.POST, instance=negocio.datos_fiscales)
        datos_domicilio_form = DatosDomicilioForm(request.POST, instance=negocio.datos_domicilio)
        datos_contacto_form = DatosContactoForm(request.POST, instance=negocio.datos_contacto)

        if (
            negocio_form.is_valid()
            and datos_fiscales_form.is_valid()
            and datos_domicilio_form.is_valid()
            and datos_contacto_form.is_valid()
        ):
            datos_fiscales_form.save()
            datos_domicilio_form.save()
            datos_contacto_form.save()
            negocio.save()

            messages.success(request, "Información del negocio actualizada correctamente.")
            return redirect("editar_negocio")

    else:
        negocio_form = NegocioForm(instance=negocio)
        datos_fiscales_form = DatosFiscalesForm(instance=negocio.datos_fiscales)
        datos_domicilio_form = DatosDomicilioForm(instance=negocio.datos_domicilio)
        datos_contacto_form = DatosContactoForm(instance=negocio.datos_contacto)

    contexto = {
        "titulo": "Editar Información del Negocio",
        "action_url": reverse("editar_negocio"),  
        "boton_texto": "Guardar Cambios",  
        "formularios": [
            (datos_fiscales_form, "Datos Fiscales"),
            (datos_domicilio_form, "Domicilio Fiscal"),
            (datos_contacto_form, "Datos de Contacto"),
        ],
    }

    return render(request, "crud/formulario_base.html", contexto)
