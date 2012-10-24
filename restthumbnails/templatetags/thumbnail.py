from django.template import Library

from restthumbnails.helpers import get_thumbnail


register = Library()

@register.assignment_tag(takes_context=True)
def thumbnail(context, source, size):
    return get_thumbnail(source, size)
