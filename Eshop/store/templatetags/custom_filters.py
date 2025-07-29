from django import template

register = template.Library()

@register.filter()
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), 0)  # default to 0 if key not found

@register.filter()
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

