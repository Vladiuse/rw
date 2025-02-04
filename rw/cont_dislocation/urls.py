from django.urls import path
from . import views


app_name = 'cont_dislocation'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.ContainerDislocationView.as_view(), name='index'),
]