from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from .models import Student, StudentRegs, Course, Deadline, TwoFactorCode
from django.db import models
from django.contrib import messages
from django.utils import timezone
from .helpers import admin_check,send_2fa_code

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']


        if password1 != password2:
            return render(request, 'registration/register.html', {'error': 'Passwords do not match'})
        if Student.objects.filter(username=username).exists():
            return render(request, 'registration/register.html', {'error': 'Username already exists'})
        if Student.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {'error': 'Email already exists'})

        user = Student.objects.create(
            username=username,
            name=name,
            email=email,
            password=make_password(password1)
        )
        user.save()
        return redirect('login')
    return render(request, 'registration/register.html')




def login_view(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user is not None:
            send_2fa_code(user)
            request.session['pre_2fa_user_id'] = user.id
            return redirect('verify_2fa')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid email or password'})
    return render(request, 'registration/login.html')


def verify_2fa_view(request):
    if request.method == 'POST':
        code = request.POST['code']
        user_id = request.session.get('pre_2fa_user_id')
        if not user_id:
            return redirect('login')

        user = Student.objects.get(id=user_id)
        try:
            two_factor_code = TwoFactorCode.objects.get(user=user, code=code, used=False, expiration_time__gt=timezone.now())
            two_factor_code.used = True
            two_factor_code.save()
            auth_login(request, user)
            return redirect('home')
        except TwoFactorCode.DoesNotExist:
            return render(request, 'registration/verify_2fa.html', {'error': 'Invalid or expired 2FA code'})
    return render(request, 'registration/verify_2fa.html')


def logout_view(request):
    logout(request)
    return redirect('login')



@login_required(login_url='/login/')
def home(request):
    student = request.user

    return render(request, 'registration/home.html', {
        'student': student
    })

@login_required(login_url='/login/')
def course_search_and_list(request):
    query = request.GET.get('q')
    student = request.user

   
    registered_courses = StudentRegs.objects.filter(student=student).values_list('course', flat=True)

  
    eligible_courses = Course.objects.filter(
        models.Q(prerequisites__isnull=True) | models.Q(prerequisites__in=registered_courses)
    ).distinct()

    if query:
        results = eligible_courses.filter(
            models.Q(code__icontains=query) |
            models.Q(name__icontains=query) |
            models.Q(instructor__icontains=query)
        )
    else:
        results = eligible_courses

    return render(request, 'registration/course_search.html', {
        'query': query,
        'results': results
    })






@login_required(login_url='/login/')
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    prerequisites = course.prerequisites.all()
    available_spots = course.capacity - StudentRegs.objects.filter(course=course).count()
    student = request.user

    already_registered = StudentRegs.objects.filter(student=student, course=course).exists()
    registration_possible = not already_registered and available_spots > 0
    deadline_passed = False

    
    try:
        add_drop_deadline = Deadline.objects.get(name="adding/dropping courses")
    except Deadline.DoesNotExist:
        add_drop_deadline = None

    if add_drop_deadline and add_drop_deadline.deadline_date < timezone.now():
        registration_possible = False
        deadline_passed = True

    if request.method == 'POST':
        if 'register' in request.POST and registration_possible:
            if already_registered:
                messages.error(request, 'You are already registered for this course.')
            elif available_spots <= 0:
                messages.error(request, 'This course is already full.')
            if deadline_passed:
                messages.error(request, 'The deadline for adding or dropping courses has passed.')
            else:
                # Check for prerequisites
                missing_prereqs = [prereq for prereq in prerequisites if not StudentRegs.objects.filter(student=student, course=prereq).exists()]
                if missing_prereqs:
                    messages.error(request, 'You have not completed the required prerequisites for this course.')
                else:
                    # Check for schedule clash
                    registered_courses = StudentRegs.objects.filter(student=student).select_related('course')
                    schedule_clash = any(
                        reg_course.course.schedule.days == course.schedule.days and
                        reg_course.course.schedule.start_time < course.schedule.end_time and
                        course.schedule.start_time < reg_course.course.schedule.end_time
                        for reg_course in registered_courses
                    )
                    if schedule_clash:
                        messages.error(request, 'This course conflicts with your current schedule.')
                    else:
                        StudentRegs.objects.create(student=student, course=course)
                        messages.success(request, 'You have successfully registered for this course.')
                        available_spots = course.capacity - StudentRegs.objects.filter(course=course).count()
                        already_registered = StudentRegs.objects.filter(student=student, course=course).exists()
                        registration_possible = not already_registered and available_spots > 0

        if 'unregister' in request.POST and already_registered:
            StudentRegs.objects.filter(student=student, course=course).delete()
            messages.success(request, 'You have successfully unregistered from this course.')
            available_spots = course.capacity - StudentRegs.objects.filter(course=course).count()
            already_registered = StudentRegs.objects.filter(student=student, course=course).exists()
            registration_possible = not already_registered and available_spots > 0

    return render(request, 'registration/course_detail.html', {
        'course': course,
        'prerequisites': prerequisites,
        'available_spots': available_spots,
        'already_registered': already_registered,
        'registration_possible': registration_possible,
        'deadline_passed': deadline_passed,
    })




@login_required(login_url='/login/')
def current_schedule(request):
    student = request.user
    registrations = StudentRegs.objects.filter(student=student)
    courses = [reg.course for reg in registrations]
    days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    schedule_data = []
    for course in courses:
        course_schedule = {
            'course_name': course.name,
            'course_code': course.code,
            'days': {day: '' for day in days_of_week},
            'instructor': course.instructor
        }
        schedule = course.schedule
        time_slot = f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}"
        for day in schedule.days.split(','):
            course_schedule['days'][day.strip()] = f"{time_slot} ({schedule.room_no})"
        schedule_data.append(course_schedule)
    
    return render(request, 'registration/my_courses.html', {
        'schedule_data': schedule_data,
        'days_of_week': days_of_week
    })

@login_required(login_url='/login/')
@user_passes_test(admin_check,login_url='/login/')
def analytics_and_reports_view(request):
    courses = Course.objects.all()
    report_data = []
    course_names = []
    enrollments = []

    for course in courses:
        enrolled_students = StudentRegs.objects.filter(course=course).count()
        report_data.append({
            'course_name': course.name,
            'course_code': course.code,
            'enrolled_students': enrolled_students,
        })
        course_names.append(course.name)
        enrollments.append(enrolled_students)
    
    return render(request, 'registration/analytics_and_reports.html', {
        'report_data': report_data,
        'course_names': course_names,
        'enrollments': enrollments,
    })