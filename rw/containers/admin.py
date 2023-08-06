from django.contrib import admin

from .models import ClientsReport, WordDoc, ClientUser, FaceProxy


class ClientDocAdmin(admin.ModelAdmin):
    list_display = ['pk','name', 'document_date', 'description', 'client_container_doc']
    exclude = ['document']
    date_hierarchy = 'document_date'

class WordDocAdmin(admin.ModelAdmin):
    list_display = ['pk','word_doc_file', 'is_doc_readable', 'hand_text_file']

class FaceClientInline(admin.TabularInline):
    model = FaceProxy
    extra = 1


class ClientAdmin(admin.ModelAdmin):
    list_display = ['pk', 'client_name', 'user', 'client_filter']
    inlines = [FaceClientInline,]

class FaceProxyAdmin(admin.ModelAdmin):
    list_display = ['name', 'attorney', 'client']


admin.site.register(ClientsReport, ClientDocAdmin)
admin.site.register(WordDoc, WordDocAdmin)
admin.site.register(ClientUser, ClientAdmin)
admin.site.register(FaceProxy, FaceProxyAdmin)
