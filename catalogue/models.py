from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db.models import JSONField
from django.utils import timezone
from django.forms.models import model_to_dict
import traceback


class User(AbstractUser, PermissionsMixin):
    country = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    phone_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.username


class DailyMetric(models.Model):
    date = models.DateField(default=timezone.now)
    active_users = models.ManyToManyField(User, related_name='active_on_date',default=[])
    new_logins = models.ManyToManyField(User, related_name='logged_in_on_date',default=[])
    new_registrations = models.ManyToManyField(User, related_name='new_registrations',default=[])

    def to_dict(self):
        return {
            "date": str(self.date),
            "new_logins":self.new_logins.count(),
            "active_users": self.active_users.count(),
            "new_registrations":self.new_registrations.count()
        }

class MediaMetric(models.Model):
    date = models.DateField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=10, choices=(('movie','Movie'),('tv','TV')))
    media_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('user', 'type', 'id')

class HistoryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField(default=dict)
    object_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {"user": str(self.user), "content": self.content, "id": self.object_id, "timestamp": self.timestamp}



class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField(default=dict)
    object_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def to_dict(self):
        return {"user": str(self.user), "content": self.content, "id": self.object_id, "timestamp": self.timestamp}

class Source(models.Model):
    type = models.CharField(max_length=10)
    tmdb_id = models.IntegerField()
    # Use StreamingServiceSerializer to serialize data for json_data
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def to_json(self):
        source_dict = self.json_data
        return source_dict

    def __str__(self):
        return f"SourcesData created on {self.date_created}"


class Review(models.Model):
    type = models.CharField(max_length=10)
    tmdb_id = models.IntegerField()

    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def to_json(self):
        return self.json_data

    def __str__(self):
        return f"SourcesData created on {self.date_created}"


class CastMember(models.Model):
    name = models.CharField(max_length=255)
    adult = models.BooleanField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True, unique=True)
    known_for_department = models.CharField(max_length=255, null=True, blank=True)
    original_name = models.CharField(max_length=255, null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    profile_path = models.CharField(max_length=255, null=True, blank=True)
    cast_id = models.IntegerField(null=True, blank=True)
    character = models.CharField(max_length=255, null=True, blank=True)
    credit_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    def to_json(self):
        source_dict = model_to_dict(self)
        return source_dict


class Title(models.Model):
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    plot_overview = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)  # Assuming 'tv_series' is the maximum length
    runtime_minutes = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    imdb_id = models.CharField(max_length=20, null=True, blank=True)
    genres = models.JSONField(null=True, blank=True)
    user_rating = models.FloatField(null=True, blank=True)
    critic_score = models.FloatField(null=True, blank=True)
    poster = models.URLField(null=True, blank=True)
    backdrop = models.URLField(null=True, blank=True)
    original_language = models.CharField(max_length=5, null=True, blank=True)
    similar_titles = models.JSONField(null=True, blank=True)
    relevance_percentile = models.FloatField(null=True, blank=True)
    trailer = models.URLField(null=True, blank=True)
    trailer_thumbnail = models.URLField(null=True, blank=True)
    certifications = models.JSONField(null=True, blank=True)

    sources = models.OneToOneField(Source, on_delete=models.CASCADE)
    cast = models.ManyToManyField(CastMember)

    def to_json(self):
        try:
            title_dict = model_to_dict(self)
            title_dict['sources'] = self.sources.to_json()
            title_dict['cast'] = [i.to_json() for i in self.cast.all()]
            return title_dict
        except Exception as _:
            traceback.print_exc()


    def __str__(self):
        return self.title


class TopRated(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"


class Releases(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"


class Trending(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"


class Upcoming(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"

class TvTrending(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"


class TvAiringToday(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"

class TvOnTheAir(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"

class TvPopular(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"

class TvTopRated(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"JsonData created on {self.date_created}"

class SourceLogos(models.Model):
    json_data = JSONField()
    date_created = models.DateTimeField(default=timezone.now)

    def to_json(self):
        source_dict = self.json_data
        # print(f'\n\n\n{source_dict}\n\n\n')
        return source_dict
    
    def __str__(self):
        return f"JsonData created on {self.date_created}"
