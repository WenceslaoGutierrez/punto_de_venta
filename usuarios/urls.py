from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import login_view, dashboard, lista_usuarios, agregar_usuario, editar_usuario, eliminar_usuario

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path("lista/", lista_usuarios, name="lista_usuarios"),
    path("agregar/", agregar_usuario, name="agregar_usuario"),
    path("editar/<int:user_id>", editar_usuario, name="editar_usuario"),
    path("eliminar/<int:user_id>/", eliminar_usuario, name="eliminar_usuario"),
]
