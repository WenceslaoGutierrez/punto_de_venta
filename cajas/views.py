from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Caja, CajaApertura
from .forms import CajaForm, CajaAperturaForm
from usuarios.utils import es_administrador, solo_administrador
from django.utils.timezone import now
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.utils.timezone import localtime



# Create your views here.

#CRUD de las cajas

#READ (General para vendedor y administrador)
@login_required
def lista_cajas(request):
    query = request.GET.get("q", "").strip()
    filtro = request.GET.get("filtro", "todos").strip()

    cajas = Caja.objects.all()

    if query:
        cajas = cajas.filter(nombre__icontains=query)

    if filtro and filtro != "todos":
        cajas = cajas.filter(estado=filtro)

    es_admin = es_administrador(request.user)

    # AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = {
            "objetos": []
        }
        for caja in cajas:
            if caja.estado == "ABIERTA":
                apertura_activa = caja.obtener_apertura_activa()
            else:
                apertura_activa = CajaApertura.objects.filter(caja=caja).order_by("-fecha_apertura").first()

            modales_html = render_to_string(
                "cajas/modales.html",
                {
                    "caja": caja,
                    "caja_apertura_form": CajaAperturaForm(initial={"caja": caja}),
                    "url_abrir": reverse("abrir_caja", args=[caja.id]),
                    "url_cerrar": reverse("cerrar_caja", args=[caja.id]),
                },
                request=request
            )

            data["objetos"].append({
                "id": caja.id,
                "campos": [
                    caja.clave,
                    caja.nombre,
                    caja.estado,
                    apertura_activa.vendedor.username if apertura_activa else "-",
                    localtime(apertura_activa.fecha_apertura).strftime("%Y-%m-%d %H:%M") if apertura_activa else "-",
                    localtime(apertura_activa.fecha_cierre).strftime("%Y-%m-%d %H:%M") if apertura_activa and apertura_activa.fecha_cierre else "Sesión en curso" if apertura_activa and apertura_activa.caja.estado == "ABIERTA" else "-",
                    f"${apertura_activa.monto_inicial:.2f}" if apertura_activa else "-",
                    f"${apertura_activa.monto_final:.2f}" if apertura_activa else "-",
                ],
                "estado": caja.estado,
                "editar_url": reverse("editar_caja", args=[caja.id]) if es_admin else None,
                "eliminar_url": reverse("eliminar_caja", args=[caja.id]) if es_admin else None,
                "abrir_url": reverse("abrir_caja", args=[caja.id]) if caja.estado == "CERRADA" else None,
                "cerrar_url": reverse("cerrar_caja", args=[caja.id]) if caja.estado == "ABIERTA" else None,
                "extra_acciones": (
                    f'<button class="btn btn-success btn-sm abrir-caja" data-id="{caja.id}" data-nombre="{caja.nombre}" data-usuario="{request.user.username}" data-url="{reverse("abrir_caja", args=[caja.id])}" {"disabled" if caja.estado == "ABIERTA" else ""}>Abrir Caja</button>'
                    f'&nbsp;'
                    f'<button class="btn btn-warning btn-sm cerrar-caja" data-id="{caja.id}" data-nombre="{caja.nombre}" data-usuario="{request.user.username}" data-url="{reverse("cerrar_caja", args=[caja.id])}" {"disabled" if caja.estado == "CERRADA" else ""}>Cerrar Caja</button>'
                ),
                "modales_extras": modales_html,
            })

        data["encabezados"] = ["Clave", "Nombre", "Estado", "Abierto por","Fecha y hora de apertura", "Hora de cierre","Monto inicial", "Monto final"]
        data["es_admin"] = es_admin
        return JsonResponse(data)

    for caja in cajas:
        caja.editar_url = reverse("editar_caja", args=[caja.id]) if es_admin else None
        caja.eliminar_url = reverse("eliminar_caja", args=[caja.id]) if es_admin else None
        caja.abrir_url = reverse("abrir_caja", args=[caja.id]) if caja.estado == "CERRADA" else None
        caja.cerrar_url = reverse("cerrar_caja", args=[caja.id]) if caja.estado == "ABIERTA" else None
        
        if caja.estado == "ABIERTA":
            caja.apertura = caja.obtener_apertura_activa()
        else:
            caja.apertura = CajaApertura.objects.filter(caja=caja).order_by("-fecha_apertura").first()

    contexto = {
        "titulo": "Cajas",
        "encabezados": [
            "Clave", "Nombre", "Estado", "Abierto por","Fecha y hora de apertura", "Hora de cierre","Monto inicial", "Monto final"],
        "campos": [
            "clave", "nombre", "estado", "apertura.vendedor.username","apertura.fecha_apertura", "apertura.fecha_cierre","apertura.monto_inicial", "apertura.monto_final"],
        "texto_boton": "Caja",
        "objetos": cajas,
        "agregar_url": reverse("agregar_caja") if es_admin else None,
        "es_admin": es_admin,
        "caja_apertura_form": CajaAperturaForm(),
    }

    return render(request, "cajas/lista_cajas.html", contexto)

#Create
@login_required
@solo_administrador
def agregar_caja(request):
    if request.method == "POST":
        caja_form = CajaForm(request.POST)

        if caja_form.is_valid():
            caja_form.save()
            messages.success(request, "Caja agregada correctamente.")
            return redirect("lista_cajas")

        else:
            form = CajaForm() 

    contexto = {
        "titulo": "Agregar Caja",
        "boton_texto": "Guardar Caja",
        "action_url": reverse("agregar_caja"),
        "formularios": [
            (CajaForm, "Datos de la Caja"),
        ],
        "volver_url": reverse("lista_cajas"),
    }

    return render(request, "crud/formulario_base.html", contexto)

#Update
@login_required
@solo_administrador
def editar_caja(request, caja_id):
    caja = get_object_or_404(Caja, id=caja_id)

    if request.method == "POST":
        caja_form = CajaForm(request.POST, instance=caja)


        if caja_form.is_valid():
            caja_form.save()
            messages.success(request, "Caja actualizada correctamente.")
            return redirect("lista_cajas")
        else:
            messages.error(request, "Error al actualizar la caja. Revisa los datos.")

    else:
        caja_form = CajaForm(instance=caja)

    contexto = {
        "titulo": "Editar Caja",
        "formularios": [
            (caja_form, "Editar Información de la Caja"),
        ],
        "boton_texto": "Guardar Cambios",
        "action_url": reverse("editar_caja", args=[caja.id]),
        "volver_url": reverse("lista_cajas")
    }

    return render(request, "crud/formulario_base.html", contexto)

#Delete
@login_required
@solo_administrador
def eliminar_caja(request, caja_id):
    caja = get_object_or_404(Caja, id=caja_id)

    if request.method == "POST":
        caja.delete()
        messages.success(request, "Caja eliminado correctamente.")
        return redirect("lista_cajas")

    return redirect("lista_cajas")

#Abir y cerrar Cajas

@login_required
def abrir_caja(request, caja_id):
    caja = get_object_or_404(Caja, id=caja_id)

    if request.method == "POST":
        monto_inicial = request.POST.get("monto_inicial")
        caja_abierta_usuario = CajaApertura.objects.filter(vendedor=request.user, fecha_cierre__isnull=True).exists()

        if caja_abierta_usuario:
            return JsonResponse({"success": False, "error": "Debes cerrar tu caja actual antes de abrir otra."})

        if CajaApertura.objects.filter(caja=caja, fecha_cierre__isnull=True).exists():
            return JsonResponse({"success": False, "error": "Esta caja ya está en uso por otro vendedor."})

        try:
            monto_inicial = float(monto_inicial)
            if monto_inicial < 0:
                raise ValueError
        except ValueError:
            return JsonResponse({"success": False, "error": "El monto inicial debe ser un número positivo."})

        nueva_apertura = CajaApertura.objects.create(
            caja=caja,
            vendedor=request.user,
            monto_inicial=monto_inicial,
            monto_vendido=0,
            monto_final=monto_inicial,
        )

        caja.estado = "ABIERTA"
        caja.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Método no permitido."})

@login_required
def cerrar_caja(request, caja_id):
    caja = get_object_or_404(Caja, id=caja_id)
    apertura = CajaApertura.objects.filter(caja=caja, caja__estado="ABIERTA").order_by("-fecha_apertura").first()

    if not apertura:
        return JsonResponse({"success": False, "error": "No hay apertura activa para esta caja."})

    if not apertura.puede_cerrar(request.user):
        return JsonResponse({"success": False, "error": "No tienes permisos para cerrar esta caja."})

    if request.method == "POST":
        try:
            apertura.cerrar_caja(request.user)
            return JsonResponse({"success": True, "message": "Caja cerrada correctamente."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido."})