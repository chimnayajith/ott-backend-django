from catalogue.models import DailyMetric, MediaMetric
from django.utils import timezone
from datetime import timedelta
from calendar import monthrange
from django.db.models import Count

def fetch_week_data():
    today = timezone.now().date()
    last_seven_days = [today - timedelta(days=i) for i in range(7)]
    last_seven_days.reverse()

    data = {
        "new_logins": {},
        "active_users": {},
        "new_registrations": {}
    }

    for day in last_seven_days:
        formatted_day = day.strftime("%d-%m-%Y")
        daily_metric = DailyMetric.objects.filter(date=day).first()
        if daily_metric:
            data["new_logins"][formatted_day] = daily_metric.new_logins.count()
            data["active_users"][formatted_day] = daily_metric.active_users.count()
            data["new_registrations"][formatted_day] = daily_metric.new_registrations.count()
        else:
            data["new_logins"][formatted_day] = 0
            data["active_users"][formatted_day] = 0
            data["new_registrations"][formatted_day] = 0

    return data


def fetch_monthly_data():
    today = timezone.now().date()
    current_year = today.year

    data = {
        "new_logins": {},
        "active_users": {},
        "new_registrations": {}
    }

    for month in range(1, 13):
        first_day = timezone.datetime(current_year, month, 1).date()
        last_day = timezone.datetime(current_year, month, monthrange(current_year, month)[1]).date()
        
        daily_metrics = DailyMetric.objects.filter(date__range=(first_day, last_day))
        
        new_logins_count = sum(metric.new_logins.count() for metric in daily_metrics)
        active_users_count = sum(metric.active_users.count() for metric in daily_metrics)
        new_registrations_count = sum(metric.new_registrations.count() for metric in daily_metrics)
        
        formatted_month = first_day.strftime("%B")
        
        data["new_logins"][formatted_month] = new_logins_count
        data["active_users"][formatted_month] = active_users_count
        data["new_registrations"][formatted_month] = new_registrations_count

    return data

def fetch_top_media():
    top_movies = (
        MediaMetric.objects.filter(type='movie')
        .values('media_id')
        .annotate(count=Count('media_id'))
        .order_by('-count')
    )
    
    top_tv_shows = (
        MediaMetric.objects.filter(type='tv')
        .values('media_id')
        .annotate(count=Count('media_id'))
        .order_by('-count')
    )
    
    data = {
        'top_movies': top_movies,
        'top_tv_shows': top_tv_shows,
    }
    
    return data