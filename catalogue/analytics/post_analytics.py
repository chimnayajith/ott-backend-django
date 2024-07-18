from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import DailyMetric, User, HistoryItem, MediaMetric
from ..signals import user_active
from datetime import date

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    daily_metrics, _ = DailyMetric.objects.get_or_create(date = date.today())
    daily_metrics.new_logins.add(user)
    daily_metrics.save()

@receiver(post_save, sender=User)
def create_registration(sender, instance, created, **kwargs):
    if created:
        daily_metrics, _ = DailyMetric.objects.get_or_create(date = date.today())
        daily_metrics.new_registrations.add(instance)
        daily_metrics.save()

@receiver(user_active)
def track_active_user(sender, user, request, **kwargs):
    daily_metrics, _ = DailyMetric.objects.get_or_create(date = date.today())
    daily_metrics.active_users.add(user)
    daily_metrics.save()

@receiver(post_save, sender=HistoryItem)
def create_history(sender, instance, created, **kwargs):
    if created:
        MediaMetric.objects.create(
            user = instance.user,
            type = instance.content["type"],
            media_id = instance.content["id"]
        )