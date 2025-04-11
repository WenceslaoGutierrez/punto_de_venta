from django.urls import path
from .views import lista_departamentos, agregar_departamento, editar_departamento, eliminar_departamento

urlpatterns = [
    path("lista/", lista_departamentos, name="lista_departamentos"),
    path("agregar/", agregar_departamento, name="agregar_departamento"),
    path("editar/<int:departamento_id>", editar_departamento, name="editar_departamento"),
    path("eliminar/<int:departamento_id>/", eliminar_departamento, name="eliminar_departamento"),
]
