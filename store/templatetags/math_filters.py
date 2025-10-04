# store/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * int(arg)
    except Exception:
        return ''
# app/templatetags/math_filters.py
from django import template
register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
