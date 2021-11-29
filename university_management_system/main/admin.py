from django.contrib import admin
from .models import AdminUser, Student

admin.site.register(Student)
admin.site.register(AdminUser)
# Register your models here.

