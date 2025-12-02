from django.db import models
from user.models import Users
from home.models import Place
# Create your models here.

class Activity(models.Model):
    class ActivityType(models.TextChoices):
        SAVED = 'saved', 'Saved'
        RECENT = 'recent', 'Recent'
        RESERVATION = 'reservation', 'Reservation'
        SAVED_DELETE = 'saved-delete', 'Saved Delete'
        RECENT_DELETE = 'recent-delete', 'Recent Delete'
        RESERVATION_DELETE = 'reservation-delete', 'Reservation Delete'

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='activity_user')
    place_id = models.CharField(max_length=255)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    place_name = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    rating = models.FloatField(blank=True, default=0)
    directions_url = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    price_currency = models.CharField(blank=True)

    activity_type = models.CharField(max_length=20, choices=ActivityType.choices, blank=True, null=True)

    is_saved = models.BooleanField(default=False)
    is_recent = models.BooleanField(default=False)
    is_reservation = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Saved"
        verbose_name_plural = "Saved"

    def __str__(self):
        return f"{self.id} -- {self.user.full_name} -- {self.place_id}"




