from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='left')
def left(value, arg):
    leng = int(arg)
    return f'{value:_<{leng}}'


@register.filter(name='right')
def right(value, arg):
    leng = int(arg)
    return f'{value:_>{leng}}'


@register.filter(name='center_dash')
def center_dash(value, arg):
    leng = int(arg)
    return f'{value:_^{leng}}'

@register.filter(name='has_group')
def has_group(user,group):
    if Group.objects.get(name=group) in user.groups.all():
        return True
    return False


@register.inclusion_tag('containers/clients/row_table.html')
def row_table(rows, id="None"):
    return {'rows': rows, 'id': id}