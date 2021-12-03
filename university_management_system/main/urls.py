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
    path("get_subtype/",views.get_subtype, name ='get_subtype'),
    path("full_attendance/",views.full_attendance, name ='full_attendance'),
    path("full_skillset/",views.full_skillset, name ='full_skillset'),
    path("result/", views.search_result, name = 'search_result'),
    path("result/<result_id>/update", views.update_result, name ='update_result'),
    path("add_result/<regi>/<course_id>", views.add_result, name='add_result'),
    path("search_student_registered/", views.search_student_registered, name = 'search_student_registered'),
    path("get_subtype_language_marks", views.get_subtype_language_marks, name = 'get_subtype_language_marks')





]