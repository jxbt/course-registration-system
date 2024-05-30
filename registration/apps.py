from django.apps import AppConfig
from django.db.models.signals import post_migrate

class RegistrationConfig(AppConfig):
    name = 'registration'

    def ready(self):
        from .populate_data import populate_courses, populate_deadlines
        post_migrate.connect(populate_courses, sender=self)
        post_migrate.connect(populate_deadlines, sender=self)
