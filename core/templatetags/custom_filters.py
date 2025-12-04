# core/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def vnd_currency(value):
    """
    Format number to Vietnamese currency
    Example: 90000 -> 90.000 VNĐ
    """
    try:
        # Convert to int
        value = int(float(value))
        # Format with thousand separator
        formatted = "{:,.0f}".format(value).replace(',', '.')
        return f"{formatted} VNĐ"
    except (ValueError, TypeError):
        return value