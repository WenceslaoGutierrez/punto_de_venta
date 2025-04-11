from django.urls import path
from .views import lista_marcas, agregar_marca, editar_marca, eliminar_marca

urlpatterns = [
    path("lista/", lista_marcas, name="lista_marcas"),
    path("agregar/", agregar_marca, name="agregar_marca"),
    path("editar/<int:marca_id>", editar_marca, name="editar_marca"),
    path("eliminar/<int:marca_id>/", eliminar_marca, name="eliminar_marca"),
]
