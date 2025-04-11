from django.urls import path
from .views import editar_negocio

urlpatterns = [
    path('negocio/editar/', editar_negocio, name='editar_negocio'),
]