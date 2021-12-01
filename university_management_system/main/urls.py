from django.urls import path
from .import views

urlpatterns = [
    path ("register/",views.registerPage, name = 'register'),
    path("login/",views.loginPage, name= "login"),
    path("logout/",views.logoutPage, name = "logout"),
    path("",views.home, name= "home"),
    path("student_home/",views.studentHome, name ="student_home"),
    path("add_student/",views.add_student, name ='add_student'),
    path("add_admin/",views.add_admin, name ='add_admin'),
    path("get_att/",views.get_att, name ='get_att'),




]