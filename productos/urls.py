from django.urls import path
from .views import lista_productos, agregar_producto, editar_producto, eliminar_producto

urlpatterns = [
    path("lista/", lista_productos, name="lista_productos"),
    path("agregar/", agregar_producto, name="agregar_producto"),
    path("editar/<int:producto_id>", editar_producto, name="editar_producto"),
    path("eliminar/<int:producto_id>/", eliminar_producto, name="eliminar_producto"),
]
