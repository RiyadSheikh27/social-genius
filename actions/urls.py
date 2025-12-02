from django.urls import path
from actions.views import *

urlpatterns = [
    path('action_places/', action_places, name="action_places"),
    path('action_places_details/', action_places_details, name="action_places_details"),
]