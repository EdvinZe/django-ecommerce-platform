from django import template
from django.utils.http import urlencode

from products.models import Category

register = template.Library()


@register.simple_tag(takes_context=True)
def change_params(context ,*args, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)