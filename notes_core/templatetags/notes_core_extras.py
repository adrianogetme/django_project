from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """
    Template filter to check if a string ends with the given argument
    Usage: {{ value|endswith:'.pdf' }}
    """
    return str(value).lower().endswith(str(arg).lower()) 