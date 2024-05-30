from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Student(AbstractUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']


class CourseSchedule(models.Model):
    days = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_no = models.CharField(max_length=50)



class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    instructor = models.CharField(max_length=255)
    capacity = models.IntegerField()
    schedule = models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)


class StudentRegs(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Deadline(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline_date = models.DateTimeField()


class EmailNotificationLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    deadline = models.ForeignKey(Deadline, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)


class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    used = models.BooleanField(default=False)
