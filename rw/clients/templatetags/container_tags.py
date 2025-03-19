from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from clients.types import UNLOADING_BOOK, CALL_TO_CLIENTS_BOOK
from django.template.loader import render_to_string
from datetime import timedelta

register = template.Library()


@register.inclusion_tag('clients/book_container_table.html')
def book_container_table(rows, id="None"):
    return {'rows': rows, 'id': id}


@register.simple_tag
def uploading_containers_table(rows, table_id):
    template = 'clients/container_tables/uploading_container_table.html'
    context = {'rows': rows, 'id': table_id}
    rendered = render_to_string(template, context)
    return format_html(rendered)


@register.simple_tag
def call_to_client_containers_table(rows, table_id):
    template =  'clients/container_tables/call_to_client_container_table.html'
    context = {'rows': rows, 'id': table_id}
    rendered = render_to_string(template, context)
    return format_html(rendered)


def timedelta_to_days(delta: timedelta) -> float:
    days = delta.days
    seconds = delta.seconds
    days += seconds / 86400
    return round(days, 2)

register.filter("timedelta_to_days", timedelta_to_days)