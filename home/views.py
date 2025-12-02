from home.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.conf import settings
import requests
from datetime import datetime, timedelta
from home.utils import *
import math
from actions.models import Activity
from system.utils import *


SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DISTANCE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
PHOTO_BASE_URL = "https://maps.googleapis.com/maps/api/place/photo"

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def current_time_and_temp(request):
    user = request.user
    serializer = TimeTempSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    lat = serializer.data.get('latitude')
    lon = serializer.data.get('longitude')

    weather_api_key = settings.OPEN_WEATHER_API
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"

    if not check_user_all_plan_limit(user=request.user, used_type='weather'):
        return Response({"error": "You have reached your plan limit for places."}, status=403)

    response = requests.get(url)
    data = response.json()

    temp_celsius = data['main']['temp']

    timestamp = data['dt']
    tz_offset = data['timezone'] 

    local_time = datetime.utcfromtimestamp(timestamp) + timedelta(seconds=tz_offset)
    day_name = local_time.strftime('%A') 
    time_str_12h = local_time.strftime('%I:%M %p')  

    if check_user_paid_subscription(user=request.user, used_type='weather'):
        increase_paid_subscription_usage(user=request.user, used_type='weather', amount=1)
    else:
        increase_free_usage(user=request.user, used_type='weather', amount=1)

    return Response({
        'status': 'succes',
        "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "image": user.image.url if user.image else None
            },
        'data': {
            'weather': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'day_name': day_name,
            'time_str': time_str_12h, 
            'temp_celsius': temp_celsius,
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_idea(request):
    serializer = GenerateIdeaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    time_str = serializer.data.get('time_str')
    temp_celsius = serializer.data.get('temp_celsius')
    weather_description = serializer.data.get('weather_description')
    day_name = serializer.data.get('day_name')
    category = serializer.data.get('category')

    if not check_user_all_plan_limit(user=request.user, used_type='ai'):
        return Response({"error": "You have reached your plan limit for places."}, status=403)

    ideas_list = ideas(temp_celsius, weather_description, day_name, time_str, category)
    
    if check_user_paid_subscription(user=request.user, used_type='ai'):
        increase_paid_subscription_usage(user=request.user, used_type='ai', amount=1)
    else:
        increase_free_usage(user=request.user, used_type='ai', amount=1)

    return Response({
        'status': 'success',
        'ideas_list': ideas_list
    }, status=status.HTTP_200_OK)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def parse_time(value):
    if not value:
        return None
    value = str(value).strip().lower()
    try:
        if value.endswith("m"):
            return float(value[:-1])
        elif value.endswith("h"):
            return float(value[:-1]) * 60
        elif value.endswith("d"):
            return float(value[:-1]) * 1440
        else:
            return float(value)
    except ValueError:
        return None

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def top_five_place(request):
    user = request.user
    # print('request user:', user, 'id:', user.id)
    lat = request.data.get("latitude")
    lng = request.data.get("longitude")
    place_type = request.data.get("place_type")
    radius = int(request.data.get("radius", 2000))
    max_time = request.data.get("max_time")
    search = request.data.get("search")
    mode = request.data.get("mode", "driving")
    open_now = request.data.get("open_now")

    if not lat or not lng or not place_type:
        return Response({"error": "latitude, longitude & place_type required"}, status=400)

    try:
        lat, lng = float(lat), float(lng)
    except ValueError:
        return Response({"error": "Latitude and longitude must be numeric"}, status=400)
    
    if not check_user_all_plan_limit(user=request.user, used_type='place'):
        return Response({"error": "You have reached your plan limit for places."}, status=403)

    max_time_min = parse_time(max_time)
    max_radius_km = radius / 1000
    all_places = []

    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": settings.GOOGLE_PLACE_API,
    }

    keywords = []
    if search: keywords.append(search)
    if request.data.get("outdoor"): keywords.append("outdoor")
    if request.data.get("vegetarian"): keywords.append("vegetarian")
    if request.data.get("bookable"): keywords.append("bookable")
    if keywords:
        params["keyword"] = " ".join(keywords)

    if open_now:
        params["opennow"] = "true"

    try:
        resp = requests.get(SEARCH_URL, params=params)
        data = resp.json()
        if data.get("status") == "OK":
            all_places.extend(data.get("results", []))
    except requests.RequestException:
        pass

    if not all_places:
        return Response({"places": []}, status=200)

    places_map = {}
    for p in all_places:
        pid = p.get("place_id")
        if not pid or pid in places_map:
            continue
 
        thumb = None
        if p.get("photos"):
            ref = p["photos"][0].get("photo_reference")
            thumb = f"{PHOTO_BASE_URL}?maxwidth=800&photoreference={ref}&key={settings.GOOGLE_PLACE_API}"

        plat = p["geometry"]["location"]["lat"]
        plng = p["geometry"]["location"]["lng"]
        dist = haversine(lat, lng, plat, plng)

        if dist > max_radius_km:
            continue


        places_map[pid] = {
            "place_id": pid,
            "name": p.get("name"),
            "latitude": plat,
            "longitude": plng,
            "rating": p.get("rating", 0),
            "reviews_count": p.get("user_ratings_total", 0),
            "thumbnail": thumb,
            "open_now": p.get("opening_hours", {}).get("open_now", None),
            "direction_url": f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={plat},{plng}",
            "types": p.get("types", []),
        }

    candidates = list(places_map.values())
    if not candidates:
        return Response({"places": []}, status=200)

    candidates.sort(key=lambda x: x["rating"] * x["reviews_count"], reverse=True)

    top_places = []

    if max_time_min:
        batch_size = 25
        i = 0
        while i < len(candidates) and len(top_places) < 5:
            batch = candidates[i:i + batch_size]
            destinations = "|".join([f"{p['latitude']},{p['longitude']}" for p in batch])

            matrix_params = {
                "origins": f"{lat},{lng}",
                "destinations": destinations,
                "mode": mode,
                "key": settings.GOOGLE_PLACE_API,
            }

            try:
                matrix_resp = requests.get(DISTANCE_URL, params=matrix_params)
                matrix_data = matrix_resp.json()
                if matrix_data.get("status") != "OK":
                    i += batch_size
                    continue

                batch_elements = matrix_data["rows"][0]["elements"]
                for j, el in enumerate(batch_elements):
                    if el.get("status") != "OK": continue
                    duration_min = el["duration"]["value"] / 60
                    distance_km = el["distance"]["value"] / 1000
                    if distance_km <= max_radius_km and duration_min <= max_time_min:
                        batch[j].update({
                            "distance_text": el["distance"]["text"],
                            "duration_text": el["duration"]["text"],
                        })
                        top_places.append(batch[j])
                        if len(top_places) >= 5:
                            break
            except requests.RequestException:
                pass

            i += batch_size

    else:
        top_places = candidates[:5]
        destinations = "|".join([f"{p['latitude']},{p['longitude']}" for p in top_places])
        matrix_params = {
            "origins": f"{lat},{lng}",
            "destinations": destinations,
            "mode": mode,
            "key": settings.GOOGLE_PLACE_API,
        }
        try:
            matrix_resp = requests.get(DISTANCE_URL, params=matrix_params)
            matrix_data = matrix_resp.json()
            if matrix_data.get("status") == "OK":
                for j, el in enumerate(matrix_data["rows"][0]["elements"]):
                    if el.get("status") == "OK":
                        top_places[j].update({
                            "distance_text": el["distance"]["text"],  
                            "duration_text": el["duration"]["text"],
                        })
        except requests.RequestException:
            pass

    # saved_ids = set(
    #     Activity.objects.filter(
    #         user=user,
    #         is_saved=True,
    #         place_id__in=[p["place_id"] for p in top_places]
    #     ).values_list("place_id", flat=True)
    # )

    # for place in top_places:
    #     place["saved"] = 1 if place["place_id"] in saved_ids else 0

    if check_user_paid_subscription(user=request.user, used_type='place'):
        increase_paid_subscription_usage(user=request.user, used_type='place', amount=1)
    else:
        increase_free_usage(user=request.user, used_type='place', amount=1)

    return Response({
        "origin": {"latitude": lat, "longitude": lng},
        "count": len(top_places),
        "places": top_places,
    })

@api_view(["POST"])
def place_details(request):
    place_id = request.data.get('place_id')
    user_lat = request.data.get('user_latitude')
    user_lng = request.data.get('user_longitude')

    if not place_id:
        return Response({"error": "place_id is required"}, status=400)
    
    if not user_lat or not user_lng:
        return Response({"error": "'user_latitude' and 'user_longitude' are required"}, status=400)

    details_params = {
        "place_id": place_id,
        "fields": "name,geometry,formatted_address,formatted_phone_number,opening_hours,website,photos",
        "key": settings.GOOGLE_PLACE_API
    }

    try:
        details_resp = requests.get(DETAILS_URL, params=details_params)
        details_data = details_resp.json()

        if details_data.get("status") != "OK":
            return Response({"error": details_data.get("status")}, status=400)

        result = details_data.get("result", {})

        main_photo_url = None
        photos = result.get("photos")
        if photos and len(photos) > 0:
            photo_reference = photos[0].get("photo_reference")
            main_photo_url = (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=800&photoreference={photo_reference}"
                f"&key={settings.GOOGLE_PLACE_API}"
            )

        today_open = None
        today_close = None
        opening_hours = result.get("opening_hours")

        if opening_hours:
            periods = opening_hours.get("periods")
            if periods:
                # Google API uses 0=Sunday, 6=Saturday
                today_index = datetime.now().weekday()  
                # print('today_index:', today_index)
                google_day_index = (today_index + 1) % 7 

                for period in periods:
                    open_info = period.get("open")
                    close_info = period.get("close")
                    if open_info and close_info and open_info.get("day") == google_day_index:
                        today_open = open_info.get("time")
                        today_close = close_info.get("time")
                        break

            elif opening_hours.get("weekday_text"):
                today_index = datetime.now().weekday() 
                weekday_text = opening_hours["weekday_text"][today_index]
                times = weekday_text.split(": ", 1)[-1]
                if "–" in times:
                    today_open, today_close = [t.strip() for t in times.split("–")]

        contact_time = None
        if today_open and today_close:
            if today_open.isdigit() and today_close.isdigit():
                today_open = f"{today_open[:2]}:{today_open[2:]}"
                today_close = f"{today_close[:2]}:{today_close[2:]}"
            contact_time = f"Today {today_open}–{today_close}"
        else:
            contact_time = "Hours not available"
        
        geometry = result.get("geometry", {}).get("location", {})
        lat = geometry.get("lat")
        lng = geometry.get("lng")   
        # print('lat,lng:', lat, lng)



        place_info = {
            "place_id": place_id,
            "thumbnail": main_photo_url,
            "name": result.get("name"),
            'contact_time': contact_time,
            "website": result.get("website"),
            "phone": result.get("formatted_phone_number"),
            "direction_url" : f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lng}&destination={lat},{lng}"
        }

        return Response(place_info, status=200)

    except requests.RequestException as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def maps_url(request):
    place_ids = request.data.get('place_ids', [])
    
    if not isinstance(place_ids, list):
        return Response({"error": "place_ids must be a list"}, status=400)
    
    maps_urls = {}
    
    for place_id in place_ids:
        maps_urls[place_id] = f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"
    
    return Response({"maps_urls": maps_urls})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_details_with_ai(request):
    place_id = request.data.get('place_id')

    if not place_id:
        return Response({"error": "place_id is required"}, status=400)
    
    if not check_user_all_plan_limit(user=request.user, used_type='ai'):
        return Response({"error": "You have reached your plan limit for places."}, status=403)

    details_params = {
        "place_id": place_id,
        "fields": "name,types,reviews,editorial_summary,formatted_address,formatted_phone_number,website,price_level,rating",
        "key": settings.GOOGLE_PLACE_API
    }

    try:
        details_resp = requests.get(DETAILS_URL, params=details_params)
        details_data = details_resp.json()

        if details_data.get("status") != "OK":
            return Response({"error": details_data.get("status")}, status=400)

        result = details_data.get("result", {})
        reviews = result.get("reviews", [])
        types = result.get("types", [])

        is_food_related = any(t in types for t in ["restaurant", "cafe", "food", "meal_takeaway"])

        description = result.get("editorial_summary", {}).get("overview", "")
        review_texts = [r.get("text", "") for r in reviews[:20] if r.get("text")]
        joined_reviews = "\n".join(review_texts) if review_texts else ""
        combined_text = description + "\n\n" + joined_reviews if description else joined_reviews
        if not combined_text:
            combined_text = "No reviews or description available."

        ai_result = analyze_reviews_with_ai(result.get("name", "Unknown Place"), types, combined_text, is_food_related)

        place_info = {
            "place_id": place_id,
            "name": result.get("name"),
            # "address": result.get("formatted_address"),
            # "phone": result.get("formatted_phone_number"),
            # "website": result.get("website"),
            "price_level": result.get("price_level"),  # 0-4
            # "overall_rating": result.get("rating"),
            "types": types,
            "ai_summary": ai_result.get("summary", []),
            "ai_ratings": ai_result.get("ratings", {})
        }

        if check_user_paid_subscription(user=request.user, used_type='ai'):
            increase_paid_subscription_usage(user=request.user, used_type='ai', amount=1)
        else:
            increase_free_usage(user=request.user, used_type='ai', amount=1)

        return Response(place_info, status=200)

    except requests.RequestException as e:
        return Response({"error": str(e)}, status=500)


