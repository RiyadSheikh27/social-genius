from django.db import models
from django.utils import timezone
from datetime import timedelta
from user.models import Users

# Create your models here.
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Free, Basic, Premium
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(blank=True, null=True)  
    place_limit = models.IntegerField(blank=True, null=True)    
    ai_limit = models.IntegerField(blank=True, null=True)
    weather_limit = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)

    feature_1 = models.CharField(max_length=255, blank=True, null=True)
    feature_2 = models.CharField(max_length=255, blank=True, null=True)
    feature_3 = models.CharField(max_length=255, blank=True, null=True)
    feature_4 = models.CharField(max_length=255, blank=True, null=True)
    feature_5 = models.CharField(max_length=255, blank=True, null=True)
    feature_6 = models.CharField(max_length=255, blank=True, null=True)
    feature_7 = models.CharField(max_length=255, blank=True, null=True)
    feature_8 = models.CharField(max_length=255, blank=True, null=True)
    feature_9 = models.CharField(max_length=255, blank=True, null=True)
    feature_10 = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super().save(*args, **kwargs)
    

class UserSubscription(models.Model): # Basic, Premium
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    used_places = models.IntegerField(default=0)
    used_ai = models.IntegerField(default=0)
    used_weather = models.IntegerField(default=0)

    is_active =  models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.email} → {self.plan.name}"

    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.plan.duration_days:
                self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
            else:
                self.end_date = None  
        super().save(*args, **kwargs)

    def is_plan_active(self):
        if self.end_date is None:
            return True
        return timezone.now() <= self.end_date

    def has_place_remaining(self):
        if self.plan.place_limit is None:  # unlimited
            return True
        return self.used_places < self.plan.place_limit


    def has_ai_remaining(self):
        if self.plan.ai_limit is None:
            return True
        return self.used_ai < self.plan.ai_limit


    def has_weather_remaining(self):
        if self.plan.weather_limit is None:
            return True
        return self.used_weather < self.plan.weather_limit

class UserFreeUsage(models.Model): 
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    used_places = models.IntegerField(default=0)
    used_ai = models.IntegerField(default=0)
    used_weather = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
        





