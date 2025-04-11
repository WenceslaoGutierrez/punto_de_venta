from django.urls import path
from .views import filtro_dinamico_productos

urlpatterns = [
    path('filtros/', filtro_dinamico_productos, name='filtro_dinamico_productos'),
]
