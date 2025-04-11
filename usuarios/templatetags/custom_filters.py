from django import template

register = template.Library()

@register.filter
def attr(obj, field_name):
    return getattr(obj, field_name, "")

@register.filter
def get_nombre(obj):
    return getattr(obj, "username", None) or getattr(obj, "nombre", "Sin nombre")
