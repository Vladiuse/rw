from django.contrib import admin

from .models import ClientsReport, WordDoc, ClientUser, FaceProxy


class ClientDocAdmin(admin.ModelAdmin):
    list_display = ['name', 'document_date', 'description', 'client_container_doc']
    exclude = ['document']
    date_hierarchy = 'document_date'

class WordDocAdmin(admin.ModelAdmin):
    list_display = ['pk','word_doc_file', 'is_doc_readable', 'hand_text_file']


admin.site.register(ClientsReport, ClientDocAdmin)
admin.site.register(WordDoc, WordDocAdmin)
admin.site.register(ClientUser)
admin.site.register(FaceProxy)
