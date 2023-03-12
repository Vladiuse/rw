from django.urls import path
from . import views

app_name = 'containers'
urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.result, name='result'),
    path('people_count', views.people_count, name='people_count'),
    path('clients', views.clients, name='clients'),
    path('create_client', views.create_client, name='create_client_doc'),
    path('client/<int:document_id>', views.client, name='show_client'),
    path('delete/<int:document_id>', views.delete, name='document_delete'),
]