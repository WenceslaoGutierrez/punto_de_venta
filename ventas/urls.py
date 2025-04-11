from django.urls import path
from .views import lista_ventas, agregar_venta, crear_venta, generar_ticket_pdf, exportar_ventas_excel

urlpatterns = [
    path("lista/", lista_ventas, name="lista_ventas"),
    path("agregar/", agregar_venta, name="agregar_venta"),
    path("crear/", crear_venta, name="crear_venta"),
    path("ticket/<int:venta_id>/", generar_ticket_pdf, name="generar_ticket_pdf"),
    path("exportar_excel/", exportar_ventas_excel, name="exportar_ventas_excel"),

]
