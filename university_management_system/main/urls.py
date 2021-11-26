from django.urls import path
from .import views
urlpatterns = [
    path ("",views.registerPage, name = 'register_page'),


]