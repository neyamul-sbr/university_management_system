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
    name = request.user.student.name
    regi = request.user.student.registration_number

    res = Result.objects.filter(student_id = regi).first()

    if res == None:
        data = []
        credits = 0
        credits_passed = 0
        percent_passed_credit = 0
        percent_registered = 0
        remain_credit =160
        remain_credit_percent= 100
    
    else:
        credits = Subject.objects.raw('''
        SELECT 1 as id, SUM(credit)
        FROM public.main_student JOIN public.main_result ON
        main_student.registration_number = main_result.student_id
        JOIN public.main_subject ON main_result.course_code = main_subject.course_code
        where main_student.registration_number=%s;''',[regi])[0].sum

        credits_passed = Subject.objects.raw('''
        SELECT 1 as id, SUM(credit)
        FROM public.main_student JOIN public.main_result ON
        main_student.registration_number = main_result.student_id
        JOIN public.main_subject ON main_result.course_code = main_subject.course_code
        where main_student.registration_number=%s and marks>=40;''',[regi])[0].sum
        percent_passed_credit = ((credits_passed)*100)/160


        percent_registered = ((credits)*100)/160

        remain_credit = 160- credits_passed

        remain_credit_percent = ((remain_credit)*100)/160
        attendance = Result.objects.raw('''
        SELECT 1 as id, subject_name as sn , attendence as attend FROM
        public.main_student JOIN public.main_result ON
        main_student.registration_number = main_result.student_id
        JOIN public.main_subject ON main_result.course_code = main_subject.course_code
        where main_student.registration_number=%s;''',[regi])
        data = []
        for i in attendance:
            data.append({
                'subject_name': i.sn,
                'attendance'  :i.attend
            })
    context ={'name':name, 
    'credits': credits,
    'percent_registered': percent_registered,
    'credits_passed' : credits_passed,
    'percent_passed_credit': percent_passed_credit,
    'remain_credit': remain_credit,
    'remain_credit_percent' : remain_credit_percent,
     
    'data'  : data,
    
    
    }
    return render(request,'student_template/index.html',context)
@login_required(login_url = 'login')
def get_att(request, *args, **kwargs):
    regi = request.user.student.registration_number
    attendance = Result.objects.raw('''
    SELECT 1 as id, subject_name as sn , attendence as attend FROM
    public.main_student JOIN public.main_result ON
    main_student.registration_number = main_result.student_id
    JOIN public.main_subject ON main_result.course_code = main_subject.course_code
    where main_student.registration_number=%s;''',[regi])
    data =[]
    labels =[]
    for i in attendance:
        labels.append(i.sn)
        data.append(i.attend)

    return JsonResponse(data={
        'labels': labels,
        'data':data,
    })
@login_required(login_url = 'login')
def get_subtype(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = Result.objects.raw('''
    SELECT 1 as id, subtype, SUM(marks) as sum_marks, count(subtype) as cnt FROM
    public.main_student JOIN public.main_result ON
    main_student.registration_number = main_result.student_id
    JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	where registration_number = %s and marks>=40
    group by subtype;''',[regi])

    data =[]
    labels =[]
    for i in subtype:
        labels.append(i.subtype)
        cntt = min(i.cnt*.5,3)
        data.append((i.sum_marks)*7/(i.cnt*100) + cntt)

    return JsonResponse(data={
        'labels': labels,
        'data':data,
    })


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
@login_required(login_url = 'login')
def full_attendance(request):
    return render(request,'student_template/full_attendance.html')
@login_required(login_url = 'login')
def full_skillset(request):
    return render(request,'student_template/full_skillset.html')


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def search_result(request):
    
    if request.method == 'POST':
        registration_number = request.POST.get('registration_number')
        course_id = request.POST.get('course_code')
        obj = Result.objects.get(student_id = registration_number ,course_code = course_id)
        id = obj.id
        return redirect(reverse('update_result', kwargs={"result_id": id}))
       
    return render(request,'admin_template/search_result.html')

def update_result(request, result_id):
    result = get_object_or_404(Result, id =result_id)
    form = UpdateForm(request.POST or None, instance = result)
    regi = result.student_id
    context = {'form':form, 'regi': regi}
    if form.is_valid():
        form.save()
    
    return render (request, 'admin_template/update_result.html',context)



def add_admin(request):
    return redirect('register')




