from django.shortcuts import render
from actions.models import Activity
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from actions.serialziers import *
from home.views import *

# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def action_places(request):
    serializer = ActivitySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    activity = serializer.save(user=request.user)

    return Response({
        "data": ActivitySerializer(activity).data,
        "message": f"{activity.activity_type} processed successfully"
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def action_places_details(request):
    user = request.user
    activities = Activity.objects.filter(user=user, is_saved=True).order_by("-updated_at")
    serializer = ActivityListSerializer(activities, many=True)
    return Response({"data": serializer.data})

