from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import LoginForm, UsuarioForm, DatosPersonalesForm, DatosContactoForm, UsuarioEdicionForm
from django.contrib.auth import get_user_model
from .models import Usuario
from django.http import JsonResponse
from usuarios.utils import solo_administrador
from django.urls import reverse



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    form = LoginForm()
    return render(request, "usuarios/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("login")


@login_required
def dashboard(request):
    usuario = request.user.perfil_usuario
    return render(request, "usuarios/dashboard.html", {"usuario": usuario})

#CRUD

#Read
@login_required
@solo_administrador
def lista_usuarios(request):
    query = request.GET.get("q", "").strip()
    filtro = request.GET.get("filtro", "todos").strip()

    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(username__icontains=query)

    if filtro and filtro != "todos":
        usuarios = usuarios.filter(rol=filtro)
    
    # Respuesta para AJAX en JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "objetos": [
                {
                    "id": u.id,
                    "campos": [u.username, u.rol],
                    "editar_url": reverse("editar_usuario", args=[u.id]),
                    "eliminar_url": reverse("eliminar_usuario", args=[u.id])
                }
                for u in usuarios
            ],
            "encabezados": ["Nombre de Usuario", "Rol"],
            "es_admin": True,
        }
        return JsonResponse(data)

    # Valores cuando no se usa AJAX
    for usuario in usuarios:
        usuario.editar_url = reverse("editar_usuario", args=[usuario.id])
        usuario.eliminar_url = reverse("eliminar_usuario", args=[usuario.id])

    contexto = {
        "titulo": "Usuarios",
        "encabezados": ["Nombre de Usuario", "Rol"],
        "campos": ["username", "rol"],
        "texto_boton": "Usuario",
        "objetos": usuarios,
        "es_admin": True,
        "agregar_url": reverse("agregar_usuario"),
    }

    return render(request, "usuarios/lista_usuarios.html", contexto)


#Create
@login_required
@solo_administrador
def agregar_usuario(request):
    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST)
        datos_personales_form = DatosPersonalesForm(request.POST)
        datos_contacto_form = DatosContactoForm(request.POST)

        if usuario_form.is_valid():
            usuario = usuario_form.save(commit=False)

            if datos_personales_form.is_valid() and any(datos_personales_form.cleaned_data.values()):
                datos_personales = datos_personales_form.save()
                usuario.datos_personales = datos_personales

            if datos_contacto_form.is_valid() and any(datos_contacto_form.cleaned_data.values()):
                datos_contacto = datos_contacto_form.save()
                usuario.datos_contacto = datos_contacto

            usuario.save()

            messages.success(request, "Usuario agregado exitosamente.")
            return redirect("lista_usuarios")
    else:
        usuario_form = UsuarioForm()
        datos_personales_form = DatosPersonalesForm()
        datos_contacto_form = DatosContactoForm()

    contexto = {
        "titulo": "Agregar Usuario",
        "boton_texto": "Guardar Usuario",
        "action_url": reverse("agregar_usuario"),
        "formularios": [
            (usuario_form, "Datos de Acceso"),
            (datos_personales_form, "Datos Personales (Opcional)"),
            (datos_contacto_form, "Datos de Contacto (Opcional)"),
        ],
        "volver_url": reverse("lista_usuarios"),
    }

    return render(request, "crud/formulario_base.html", contexto)


#Update
@login_required
@solo_administrador
def editar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == "POST":
        usuario_form = UsuarioEdicionForm(request.POST, instance=usuario)
        datos_personales_form = DatosPersonalesForm(request.POST, instance=usuario.datos_personales)
        datos_contacto_form = DatosContactoForm(request.POST, instance=usuario.datos_contacto)

        if usuario_form.is_valid():
            usuario = usuario_form.save(commit=False)
            usuario.username = usuario_form.cleaned_data["username"]

            if datos_personales_form.is_valid():
                datos_personales = datos_personales_form.save(commit=False)
                if not usuario.datos_personales:
                    usuario.datos_personales = datos_personales
                datos_personales.save()

            if datos_contacto_form.is_valid():
                datos_contacto = datos_contacto_form.save(commit=False)
                if not usuario.datos_contacto:
                    usuario.datos_contacto = datos_contacto
                datos_contacto.save()

            usuario.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("lista_usuarios")

        else:
            messages.error(request, "Por favor corrige los errores.")

    else:
        usuario_form = UsuarioEdicionForm(instance=usuario)
        datos_personales_form = DatosPersonalesForm(instance=usuario.datos_personales)
        datos_contacto_form = DatosContactoForm(instance=usuario.datos_contacto)

    contexto = {
        "titulo": f"Editar Usuario - {usuario.username}",
        "boton_texto": "Actualizar Usuario",
        "action_url": reverse("editar_usuario", args=[usuario.id]),
        "formularios": [
            (usuario_form, "Datos de Acceso"),
            (datos_personales_form, "Datos Personales (Opcional)"),
            (datos_contacto_form, "Datos de Contacto (Opcional)"),
        ],
        "volver_url": reverse("lista_usuarios"),
    }

    return render(request, "crud/formulario_base.html", contexto)

    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == "POST":
        usuario_form = UsuarioEdicionForm(request.POST, instance=usuario)
        datos_personales_form = DatosPersonalesForm(request.POST, instance=usuario.datos_personales)
        datos_contacto_form = DatosContactoForm(request.POST, instance=usuario.datos_contacto)

        if usuario_form.is_valid():
            usuario = usuario_form.save(commit=False)
            usuario.username = usuario_form.cleaned_data["username"]

            if datos_personales_form.is_valid():
                datos_personales = datos_personales_form.save(commit=False)
                if not usuario.datos_personales:
                    usuario.datos_personales = datos_personales
                datos_personales.save()

            if datos_contacto_form.is_valid():
                datos_contacto = datos_contacto_form.save(commit=False)
                if not usuario.datos_contacto:
                    usuario.datos_contacto = datos_contacto
                datos_contacto.save()

            usuario.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("lista_usuarios")

        else:
            messages.error(request, "Por favor corrige los errores.")

    else:
        usuario_form = UsuarioEdicionForm(instance=usuario)
        datos_personales_form = DatosPersonalesForm(instance=usuario.datos_personales)
        datos_contacto_form = DatosContactoForm(instance=usuario.datos_contacto)

    return render(
        request,
        "usuarios/editar_usuario.html",
        {
            "usuario_form": usuario_form,
            "datos_personales_form": datos_personales_form,
            "datos_contacto_form": datos_contacto_form,
        },
    )

#Delete
@login_required
@solo_administrador
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect("lista_usuarios")

    return redirect("lista_usuarios")