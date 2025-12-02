from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
# Create your models here.

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    otp_expired_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.otp_expired_at = timezone.now() + timedelta(minutes=5)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} || {self.otp} || {self.otp_expired_at}"

class Users(AbstractUser):
    # username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email
