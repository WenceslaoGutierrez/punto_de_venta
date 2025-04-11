from django.shortcuts import render
from productos.models import Producto
from django.db.models import Q
from datetime import time, date

def obtener_productos_filtrados(request):
    query_params = request.GET
    filtros = Q()
    q_param = query_params.get('q')

    # Filtros tipo Q
    if q_param:
        or_grupos = q_param.split('|')
        q_total = Q()
        for grupo in or_grupos:
            and_filtros = grupo.split('&')
            q_grupo = Q()
            for filtro in and_filtros:
                if '=' not in filtro:
                    continue
                campo, valor = filtro.split('=', 1)
                if '__in' in campo:
                    valor = valor.split(',')
                q_grupo &= Q(**{campo: valor})
            q_total |= q_grupo
        filtros &= q_total

    # Filtros simples
    for key, value in query_params.items():
        if key == 'q' or value.strip() == '':
            continue
        if '__in' in key:
            value = value.split(',')
        filtros &= Q(**{key: value})

    return Producto.objects.filter(filtros)

def filtro_dinamico_productos(request):
    productos = obtener_productos_filtrados(request)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'pruebas/tabla_productos.html', {'productos': productos})

    return render(request, 'pruebas/filtros.html', {
        'productos': productos,
        'parametros': request.GET
    })
