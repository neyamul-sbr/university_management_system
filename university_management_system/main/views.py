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
from .forms import CreateUserForm
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
        

    return render(request, 'login_template/basic_elements.html')
@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name = 'student')
            user.groups.add(group)


            messages.success(request, 'Account is created for ' + username)
            return redirect('login')

    context = {'form':form}
    return render(request,'registration_template/basic_elements.html',context)

def logoutPage(request):
    logout(request)
    return redirect('login') 
@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def home(request):
    return render(request,'student_template/index.html')

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['student'])
def studentHome(request):
    # name = request.user.student.name.all()
    # context ={'name':name}
    return render(request,'student_template/index.html')
