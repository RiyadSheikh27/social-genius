from django.db import models

# Create your models here.
class Place(models.Model):
    place_id = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    best_reason = models.TextField(blank=True)
    image = models.URLField(blank=True)
    place_type = models.CharField(max_length=255, blank=True) # restaurant, cafee
    rating = models.FloatField(blank=True, default=0)
    review = models.FloatField(blank=True, default=0)
    distance_km = models.FloatField(blank=True)
    distance_time = models.CharField(blank=True)
    directions_url = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    price_currency = models.CharField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.place_id} -- {self.name}"


