from django.contrib import admin

from .models import ClientDoc


class ClientDocAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_date', 'description', 'document_file', 'area_document']
    exclude = ['document']
    date_hierarchy = 'document_date'

admin.site.register(ClientDoc, ClientDocAdmin)
