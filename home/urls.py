from django.urls import path
from home.views import *

urlpatterns = [
    path('time-temp/', current_time_and_temp, name='current_time_and_temp'),
    path('generate-idea/', generate_idea, name='generate_idea'),
    path('top-five-place-list/', top_five_place, name='top_five_place'),
    path('place-details/', place_details, name='place_details'),
    path('maps-urls/', maps_url, name='maps_urls'),
    path('place-details-with-ai/', place_details_with_ai, name="place_details_with_ai")

]
