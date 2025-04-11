from django.urls import path
from .views import lista_cajas, agregar_caja, editar_caja, eliminar_caja, abrir_caja, cerrar_caja

urlpatterns = [
    path("lista/", lista_cajas, name="lista_cajas"),
    path("agregar/", agregar_caja, name="agregar_caja"),
    path("editar/<int:caja_id>/", editar_caja, name="editar_caja"),
    path("eliminar/<int:caja_id>/", eliminar_caja, name="eliminar_caja"),
    path("abrir/<int:caja_id>/", abrir_caja, name="abrir_caja"),
    path("cerrar/<int:caja_id>/", cerrar_caja, name="cerrar_caja"),
]
