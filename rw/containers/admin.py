from django.contrib import admin

from .models import ClientDoc


class ClientDocAdmin(admin.ModelAdmin):
    list_display = ['name', 'load_date', 'document_date', 'description', 'document_file']
    exclude = ['document']
    date_hierarchy = 'document_date'

admin.site.register(ClientDoc, ClientDocAdmin)
