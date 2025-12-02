from rest_framework import serializers

class TimeTempSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

class GenerateIdeaSerializer(serializers.Serializer):
    time_str = serializers.CharField(required=True)
    temp_celsius = serializers.CharField(required=True)
    weather_description = serializers.CharField(required=True)
    day_name = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
   






