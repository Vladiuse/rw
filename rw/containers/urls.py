from django.urls import path
from . import views

app_name = 'containers'
urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.result, name='result'),
    path('people_count', views.people_count, name='people_count'),
    path('clients', views.clients_documents, name='clients'),
    path('create_client', views.create_client, name='create_client_doc'),
    path('client/<int:document_id>', views.clients_document, name='show_client'),
    path('client_document/<int:document_id>', views.client_document, name='client_document'),
    path('delete/<int:document_id>', views.delete, name='document_delete'),
    path('client_check_docs/<int:client_report_id>', views.client_check_docs, name='client_check_docs'),
    path('add_hand_text_to_docs/<int:document_id>', views.add_hand_text_to_docs, name='add_hand_text_to_docs'),
    path('files_no_data_rows/<int:file_id>', views.files_no_data_rows, name='files_no_data_rows'),
    path('print_document/<int:client_container_id>', views.print_document, name='print_document'),

    path('test', views.test, name='test'),
]