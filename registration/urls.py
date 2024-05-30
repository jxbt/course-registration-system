from django.urls import path
from .views import register,login_view,logout_view,home, course_search_and_list, course_detail, current_schedule,analytics_and_reports_view,verify_2fa_view

urlpatterns = [
    path('',home,name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('verify_2fa/', verify_2fa_view, name='verify_2fa'),
    path('logout/', logout_view, name='logout'),
    path('courses/',course_search_and_list, name='course_search_and_list'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('my_courses/', current_schedule, name='my_courses'),
    path('analytics_and_reports/', analytics_and_reports_view, name='analytics_and_reports')
]
