from django.urls import path
from . import views


app_name = 'clients'
urlpatterns = [
    path('', views.index, name='index'),
    path('load-book/', views.LoadBookFileView.as_view(), name='load_book'),
    path('book-list/', views.book_list, name='book_list'),
    path('book-list/book-<int:book_id>/', views.book_detail, name='book_detail'),
    path('book-list/book-delete-<int:book_id>/', views.book_delete, name='book_delete'),
    path('book-list/book-original-text-<int:book_id>/', views.book_file_original_text, name='book_file_original_text'),
    path('book-list/<int:book_id>/', views.book_no_containers_data, name='book_no_containers_data'),
    path('test/', views.test,),
]