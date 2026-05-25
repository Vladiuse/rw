from datetime import timedelta
from typing import Any

from django import template
from django.template.loader import render_to_string
from django.utils.html import format_html

register = template.Library()


@register.inclusion_tag("clients/book_container_table.html")
def book_container_table(rows, id="None"):
    return {"rows": rows, "id": id}


@register.simple_tag
def uploading_containers_table(rows, table_id):
    template = "clients/container_tables/uploading_container_table.html"
    context = {"rows": rows, "id": table_id}
    rendered = render_to_string(template, context)
    return format_html(rendered)


@register.simple_tag
def call_to_client_containers_table(rows, table_id):
    template = "clients/container_tables/call_to_client_container_table.html"
    context = {"rows": rows, "id": table_id}
    rendered = render_to_string(template, context)
    return format_html(rendered)


def timedelta_to_days(delta: timedelta) -> str:
    days = delta.days
    seconds = delta.seconds
    days += seconds / 86400
    result_string = str(round(days, 2))
    return result_string.replace(".", ",")


def to_excel_format(value: Any) -> str:  # noqa: ANN401
    return str(value).replace(".", ",")


register.filter("timedelta_to_days", timedelta_to_days)
register.filter("to_excel_format", to_excel_format)
