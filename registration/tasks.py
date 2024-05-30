import os
from celery import shared_task
from django.utils import timezone
from .models import Deadline, Student, EmailNotificationLog
from .helpers import send_mail

@shared_task
def check_deadlines_and_notify():
    current_time = timezone.now()
    two_days_later = current_time + timezone.timedelta(days=2)
    notify_duration_hours = float(os.getenv('NOTIFY_DURATION_IN_HOURS', 1))
    n_hours_ago = current_time - timezone.timedelta(hours=notify_duration_hours)

    upcoming_deadlines = Deadline.objects.filter(deadline_date__lte=two_days_later, deadline_date__gte=current_time)


    if upcoming_deadlines.exists():
        students = Student.objects.all()
        for deadline in upcoming_deadlines:

            for student in students:
                last_notification = EmailNotificationLog.objects.filter(student=student, deadline=deadline, sent_at__gte=n_hours_ago).exists()
                if not last_notification:
                    description = f"{deadline.description}\n\nDeadline Date (UTC): {deadline.deadline_date.strftime('%Y-%m-%d %H:%M:%S %Z')}"

                    send_mail(
                        student.email,
                        f'CoursesReg - Reminder: {deadline.name} is approaching',
                        description
                    )
                    EmailNotificationLog.objects.create(student=student, deadline=deadline)

                else:
                    pass
    else:
        pass
