from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Event, Attendance

@receiver(post_save, sender=Event)
def create_attendance_for_event(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            Attendance.objects.create(event=instance, user=user)
