from django.utils import timezone
from .models import Course, CourseSchedule,Deadline


def populate_deadlines(sender, **kwargs):
    if Deadline.objects.count() == 0:
        deadline_date = timezone.now() + timezone.timedelta(days=1)
        Deadline.objects.create(
            name="adding/dropping courses",
            description="The ability to add or drop courses from your schedule is ending soon!",
            deadline_date=deadline_date
        )

def populate_courses(sender, **kwargs):
    if Course.objects.count() == 0:
        schedule1 = CourseSchedule.objects.create(
            days="Sunday, Tuesday, Thursday",
            start_time="08:00:00",
            end_time="09:00:00",
            room_no="101"
        )



        schedule2 = CourseSchedule.objects.create(
            days="Monday, Wednesday",
            start_time="09:00:00",
            end_time="10:00:00",
            room_no="102"
        )

        schedule3 = CourseSchedule.objects.create(
            days="Monday, Wednesday",
            start_time="10:00:00",
            end_time="11:00:00",
            room_no="103"
        )


        cse101 = Course.objects.create(
            code="CSE101", 
            name="Introduction to Computer Science", 
            description="Basics of computer science", 
            instructor="Dr. Ameer Ahmad", 
            capacity=30, 
            schedule=schedule2
        )
        
        cse102 = Course.objects.create(
            code="CSE102", 
            name="Data Structures", 
            description="Introduction to data structures", 
            instructor="Dr. Nabel Mohammad", 
            capacity=25, 
            schedule=schedule3
        )
        
        courses = [
            {"code": "CSE103", "name": "Algorithms", "description": "Basic algorithms", "instructor": "Dr. Ahmad Ammer", "capacity": 20, "schedule": schedule1},
            {"code": "CSE104", "name": "Operating Systems", "description": "Introduction to operating systems", "instructor": "Dr. Mohammad Saber", "capacity": 35, "schedule": schedule1},
            {"code": "CSE105", "name": "Database Systems", "description": "Introduction to databases", "instructor": "Dr. Ayman Saleh", "capacity": 30, "schedule": schedule1},
            {"code": "CSE106", "name": "Computer Networks", "description": "Basics of computer networks", "instructor": "Dr. Khader Jamal", "capacity": 25, "schedule": schedule2},
            {"code": "CSE107", "name": "Software Engineering", "description": "Introduction to software engineering", "instructor": "Dr. Mohammad Saber", "capacity": 20, "schedule": schedule2},
            {"code": "CSE108", "name": "Machine Learning", "description": "Basics of machine learning", "instructor": "Dr. Ayman Saleh", "capacity": 35, "schedule": schedule2},
            {"code": "CSE109", "name": "Artificial Intelligence", "description": "Introduction to AI", "instructor": "Dr. Mohammad Saber", "capacity": 30, "schedule": schedule3},
            {"code": "CSE110", "name": "Cyber Security", "description": "Basics of cyber security", "instructor": "Dr. Ahmad Ammer", "capacity": 25, "schedule": schedule3},
        ]


        for course_data in courses:
            course = Course.objects.create(**course_data)
            if course.code == "CSE103": 
                course.prerequisites.add(cse102)
            elif course.code == "CSE104": 
                course.prerequisites.add(cse101)
