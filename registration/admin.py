from django.contrib import admin
from .models import Student, Course, CourseSchedule, StudentRegs, Deadline

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(CourseSchedule)
admin.site.register(StudentRegs)
admin.site.register(Deadline)