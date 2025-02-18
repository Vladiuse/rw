from django.urls import path
from . import views


app_name = 'clients'
urlpatterns = [
    path('', views.index, name='index'),
    path('load-book/', views.load_book_file, name='load_book_file'),
]