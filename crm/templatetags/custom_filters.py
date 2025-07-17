from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_total(summary, service):
    return sum(personal_services for personal_services in summary[service].values())

@register.filter
def get_total_earnings(earnings):
    return sum(employee['total_earnings'] for employee in earnings)

