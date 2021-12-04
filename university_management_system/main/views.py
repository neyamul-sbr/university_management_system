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
from django.http import HttpResponse
from django.views.generic import View

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
 
def cal_cg(marks):
    if marks>=80:
        return 4.0
    elif marks>=75:
        return 3.75
    elif marks>=70:
        return 3.5
    elif marks>=65:
        return 3.25
    elif marks>=60:
        return 3.00
    elif marks>=55:
        return 2.75
    elif marks>=50:
        return 2.50
    elif marks>=45:
        return 2.25
    elif marks>=40:
        return 2.00
    else:
        return 0.00


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
        current_cgpa =0
    
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

        cgpa = Subject.objects.raw('''
        SELECT 1 as id, credit, marks
        FROM public.main_student JOIN public.main_result ON
        main_student.registration_number = main_result.student_id
        JOIN public.main_subject ON main_result.course_code = main_subject.course_code
        where main_student.registration_number=%s and marks>=40;''',[regi])
        upper =0
        lower = 0
        for k in cgpa:
            upper =upper+ k.credit * cal_cg(k.marks)
            lower =lower + k.credit
        
        current_cgpa = upper/lower
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
    'current_cgpa': current_cgpa,
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
def getting_json(subtype, regi):

    marksObj = Result.objects.raw('''
    SELECT 1 as id, subject_name, main_subject.course_code as cc, marks FROM
    public.main_student JOIN public.main_result ON
    main_student.registration_number = main_result.student_id
    JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	where registration_number = %s and subtype = %s;''',[regi,subtype])
    

    subject_name =[]
    course_code =[]
    marks = []
    attr = []
    attr.append("subject_name")
    attr.append("course_code")
    attr.append("marks")
    json_res =[]
    for i in marksObj:
        obj = {}
        obj[attr[0]] = i.subject_name
        print(i.subject_name)
        obj[attr[1]] = i.cc
        obj[attr[2]]= i.marks
        json_res.append(obj) 
    return json_res


def getting_json_result(regi):

    marksObj = Result.objects.raw('''
    SELECT 1 as id, subject_name, main_subject.course_code as cc, marks, attendence as attendance FROM
    public.main_student JOIN public.main_result ON
    main_student.registration_number = main_result.student_id
    JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	where registration_number = %s''',[regi])
    

    subject_name =[]
    course_code =[]
    marks = []
    attr = []
    
    attr.append("subject_name")
    attr.append("course_code")
    attr.append("marks")
    attr.append("attendance")
    attr.append("cgpa")
    json_res =[]
    for i in marksObj:
        obj = {}
        obj[attr[0]] = i.subject_name
        obj[attr[1]] = i.cc
        obj[attr[2]]= i.marks
        obj[attr[3]] = i.attendance
        cgpa = cal_cg(i.marks)
        obj[attr[4]]= cgpa
        json_res.append(obj) 
    return json_res

@login_required(login_url = 'login')
def get_subtype_networking_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "Networking"
    # subtype = Result.objects.raw('''
    # SELECT 1 as id, subtype, SUM(marks) as sum_marks, count(subtype) as cnt FROM
    # public.main_student JOIN public.main_result ON
    # main_student.registration_number = main_result.student_id
    # JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	# where registration_number = %s and marks>=40
    # group by subtype;''',[regi])

    # marksObj = Result.objects.raw('''
    # SELECT 1 as id, subject_name, main_subject.course_code as cc, marks FROM
    # public.main_student JOIN public.main_result ON
    # main_student.registration_number = main_result.student_id
    # JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	# where registration_number = %s and subtype = 'Networking';''',[regi])
    

    # subject_name =[]
    # course_code =[]
    # marks = []
    # attr = []
    # attr.append("subject_name")
    # attr.append("course_code")
    # attr.append("marks")
    # json_res =[]
    # for i in marksObj:
    #     obj = {}
    #     obj[attr[0]] = i.subject_name
    #     obj[attr[1]] = i.cc
    #     obj[attr[2]]= i.marks
    #     json_res.append(obj) 
    
    json_res = getting_json(subtype, regi)
        

    return JsonResponse(json_res, safe = False)  

@login_required(login_url = 'login')
def get_subtype_dbms_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "DBMS"
    json_res = getting_json(subtype, regi)
    return JsonResponse(json_res, safe = False) 

@login_required(login_url = 'login')
def get_subtype_ai_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "AI"
    json_res = getting_json(subtype, regi)
    return JsonResponse(json_res, safe = False)


@login_required(login_url = 'login')
def get_subtype_programming_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "Programming"
    json_res = getting_json(subtype, regi)
    return JsonResponse(json_res, safe = False)

@login_required(login_url = 'login')
def get_subtype_sys_n_media_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "System & Multimedia"
    json_res = getting_json(subtype, regi)
    return JsonResponse(json_res, safe = False) 


@login_required(login_url = 'login')
def get_subtype_project_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    subtype = "Project"
    json_res = getting_json(subtype, regi)
    return JsonResponse(json_res, safe = False) 


@login_required(login_url = 'login')
def get_all_the_marks(request, *args, **kwargs):
    regi = request.user.student.registration_number
    json_res = getting_json_result(regi)
    return JsonResponse(json_res, safe = False)


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


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def search_student_registered(request):
    
    if request.method == 'POST':
        regi = request.POST.get('registration_number')
        course_id = request.POST.get('course_code')
        res = Student.objects.filter(registration_number = regi).first()
        sub = Subject.objects.filter(course_code = course_id).first()
        if res == None:
            return HttpResponse("The Student Is not Registered.. Register The Student First")
        if sub == None:
            return HttpResponse("The Subject Is not Registered.. Register The Subject First")
        return redirect(reverse('add_result', kwargs= {"regi": regi, "course_id": course_id}))
    return render(request,'admin_template/search_student_registered.html')
        
    
       

@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def update_result(request, result_id):
    result = get_object_or_404(Result, id =result_id)
    form = UpdateForm(request.POST or None, instance = result)
    regi = result.student_id
    context = {'form':form, 'regi': regi}
    if form.is_valid():
        form.save()
    
    return render (request, 'admin_template/update_result.html',context)


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def add_result(request, regi, course_id):
    stu =  get_object_or_404(Student, registration_number = regi)
    res = Result.objects.filter(student_id = regi, course_code = course_id).first()
    if res != None:
        return HttpResponse("The result already exist!!!")

    form = AddResultForm(request.POST or None, initial ={'student': stu, 'course_code': course_id })
    context = {'form':form, 'regi': regi, 'course_id': course_id}
    if form.is_valid():
        form.save()
    return render(request, 'admin_template/add_result.html',context)


from django.http import HttpResponse
from django.views.generic import View

from main.utils import html_to_pdf 
from django.template.loader import render_to_string
from django.core.files import File
import os
#Creating a class based view
class GeneratePdf(View):
     def get(self, request, *args, **kwargs):
        regi = request.user.student.registration_number
        name = request.user.student.name
        phone = request.user.student.phone
        email = request.user.email
        data = Result.objects.raw('''
        SELECT 1 as id, subject_name, main_subject.course_code as cc, marks, attendence as attendance ,student_id as cg , credit FROM
        public.main_student JOIN public.main_result ON
        main_student.registration_number = main_result.student_id
        JOIN public.main_subject ON main_result.course_code = main_subject.course_code
	    where registration_number = %s''',[regi])

        upper =0
        lower = 0
        cgpa = 0
        status =""
        for k in data:
            if k.marks>=40:
                upper =upper+ k.credit * cal_cg(k.marks)
                lower =lower + k.credit
        
        if lower == 0:
            cgpa =0
            
        else:
            cgpa = upper/lower
        if lower<160:
            status = "Incomplete"
        else:
            status = "Complete"

        for i in data:
            i.student_id = cal_cg(i.marks)
                    

        module_dir = os.path.dirname(__file__)  # get current directory
        file_path1 = os.path.join(module_dir, 'templates/student_template/generate_result_pdf_temp.html')
        file_path2 = os.path.join(module_dir, 'templates/student_template/generate_result_pdf.html')

        pwd = os.path.dirname(__file__)
        open(file_path1, "w").write(render_to_string(file_path2, {'data': data,'regi':regi,'name':name, 'phone': phone, 'email':email,'cgpa':cgpa,'status':status }))

        # Converting the HTML template into a PDF file
        pdf = html_to_pdf(file_path1)
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')













def add_admin(request):
    return redirect('register')




