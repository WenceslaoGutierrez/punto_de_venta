from django.urls import path
from .views import lista_unidades, agregar_unidad, editar_unidad, eliminar_unidad

urlpatterns = [
    path("lista/", lista_unidades, name="lista_unidades"),
    path("agregar/", agregar_unidad, name="agregar_unidad"),
    path("editar/<int:unidad_id>", editar_unidad, name="editar_unidad"),
    path("eliminar/<int:unidad_id>/", eliminar_unidad, name="eliminar_unidad"),
]
