from django.urls import path
from .views import lista_clientes, agregar_cliente, editar_cliente, eliminar_cliente

urlpatterns = [
    path("lista/", lista_clientes, name="lista_clientes"),
    path("agregar/", agregar_cliente, name="agregar_cliente"),
    path("editar/<int:cliente_id>/", editar_cliente, name="editar_cliente"),
    path("eliminar/<int:cliente_id>/", eliminar_cliente, name="eliminar_cliente"),
]
