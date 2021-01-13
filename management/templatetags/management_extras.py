from django import template

register = template.Library()


@register.filter
def get_attr(obj, val):
    return getattr(obj, val)


@register.filter(name='tostring')
def to_string(value):
    return str(value)
