from django.urls import path
from support.views import *

urlpatterns = [
    path('help_and_support/', help_and_support, name='help_and_support'),
]