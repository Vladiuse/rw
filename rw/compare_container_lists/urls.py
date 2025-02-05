from django.urls import path
from . import views


app_name = 'compare_container_lists'
urlpatterns = [
    path('', views.index,),
    path('containers/', views.index, name='containers'),
    path('vagons', views.index, name='vagons'),
]