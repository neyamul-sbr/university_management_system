import json
from django.contrib.auth.models import Group
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import *
from django.core import management
from django.core.management.commands import loaddata

#from .EmailBackend import EmailBackend
from .models import *
from .forms import *
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from .decorators import allowed_users, unauthenticated_user

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request, "Username Or Password is not Correct")
        

    return render(request, 'login_template/login1.html')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def registerPage(request):
    user_form = CreateUserForm(request.POST or None) 
    admin_form = AdminForm(request.POST or None, request.FILES or None)
    context = {'admin_form': admin_form,'user_form':user_form, 'page_title':'add student'}
    if request.method == 'POST':
        if user_form.is_valid and admin_form.is_valid():
            user = user_form.save()
            admin = admin_form.save()
            admin.user =user
            admin.save()
            # username = student_form.cleaned_data.get('username')
            # email = student_form.cleaned_data.get('email')
            # password1 = student_form.cleaned_data.get('password1')
            # password2 = student_form.cleaned_data.get('password2')
            # name = student_form.cleaned_data.get('name')
            # name = student_form.cleaned_data.get('phone')
            # passport = request.FILES['profile_pic']
            # fs = FileSystemStorage()
            # filename = fs.save(passport.name, passport)
            # passport_url = fs.url(filename)
            group = Group.objects.get(name = 'admin')
            user.groups.add(group)
        else:
            messages.success(request, "Successfully Admin Added")
    return render(request, 'registration_template/add_admin.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login') 


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def home(request):
    return render(request,'admin_template/index.html')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['student'])
def studentHome(request):
    name = request.user.student.phone
    context ={'name':name}
    return render(request,'student_template/index.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def add_student(request):
    user_form = CreateUserForm(request.POST or None) 
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'student_form': student_form,'user_form':user_form, 'page_title':'add student'}
    if request.method == 'POST':
        if user_form.is_valid and student_form.is_valid():
            user = user_form.save()
            student = student_form.save()
            student.user =user
            student.save()
            # username = student_form.cleaned_data.get('username')
            # email = student_form.cleaned_data.get('email')
            # password1 = student_form.cleaned_data.get('password1')
            # password2 = student_form.cleaned_data.get('password2')
            # name = student_form.cleaned_data.get('name')
            # name = student_form.cleaned_data.get('phone')
            # passport = request.FILES['profile_pic']
            # fs = FileSystemStorage()
            # filename = fs.save(passport.name, passport)
            # passport_url = fs.url(filename)
            group = Group.objects.get(name = 'student')
            user.groups.add(group)
            messages.success(request, "Successfully Student Added")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'student_template/add_student.html',context)

def add_admin(request):
    return redirect('register')




