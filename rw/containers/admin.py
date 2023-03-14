from django.contrib import admin

from .models import ClientDoc, WordDoc


class ClientDocAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_date', 'description', 'client_container_doc', 'area_doc']
    exclude = ['document']
    date_hierarchy = 'document_date'

class WordDocAdmin(admin.ModelAdmin):
    list_display = ['pk','word_doc_file', 'is_read', 'result_text_file']

admin.site.register(ClientDoc, ClientDocAdmin)
admin.site.register(WordDoc, WordDocAdmin)
