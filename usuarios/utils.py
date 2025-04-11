from django.contrib.auth.decorators import user_passes_test

#AUTENTICACION ADMINISTRADOR
def es_administrador(user):
    return user.is_authenticated and user.perfil_usuario.rol == "ADMIN"

solo_administrador = user_passes_test(es_administrador, login_url='dashboard')