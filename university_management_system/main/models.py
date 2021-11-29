from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, null = True, on_delete= models.CASCADE)
    # is_admin =models.BooleanField(default= True )
    # is_student = models.BooleanField(default= False)
    name = models.CharField(max_length= 200, null= True)
    phone = models.CharField(max_length= 200, null = True)
    profile_pic = models.ImageField(null = True, blank = True)

    def __str__(self):
        return self.name

class AdminUser(models.Model):
    user = models.OneToOneField(User, null = True, on_delete= models.CASCADE)
    # is_admin =models.BooleanField(default= True )
    # is_student = models.BooleanField(default= False)
    name = models.CharField(max_length= 200, null= True)
    phone = models.CharField(max_length= 200, null = True)
    email = models.CharField(max_length=200, null = True)
    profile_pic = models.ImageField(null = True, blank = True)

    def __str__(self):
        return self.name








