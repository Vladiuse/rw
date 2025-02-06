from django.urls import path
from . import views


app_name = 'compare_container_lists'
urlpatterns = [
    path('', views.CompareListsView.as_view(),),
]