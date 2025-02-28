from django import template

register = template.Library()

@register.filter
def starts_with(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter
def remove_prefix(text, prefix):
    if isinstance(text, str) and text.startswith(prefix):
        return text[len(prefix):]
    return text 