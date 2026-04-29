from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Return the value from a dictionary using the given key."""
    if d is None:
        return None
    return d.get(key)
