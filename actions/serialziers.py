from rest_framework import serializers
from actions.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    place_id = serializers.CharField(required=True)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    place_name = serializers.CharField(required=True)
    image = serializers.URLField(required=False)
    rating = serializers.FloatField(required=True)
    directions_url = serializers.URLField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    price_currency = serializers.CharField(required=False, allow_blank=True)

    activity_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Activity.ActivityType.choices],
        required=True
    )

    class Meta:
        model = Activity
        fields = [
            "place_id",
            "latitude",
            "longitude",
            "place_name",
            "image",
            "rating",
            "directions_url",
            "phone",
            "email",
            "website",
            "price_currency",
            "activity_type",
        ]

    def create(self, validated_data):
        user = validated_data.pop("user")
        place_id = validated_data["place_id"]
        activity_type = validated_data["activity_type"]

        obj, created = Activity.objects.get_or_create(
            user=user,
            place_id=place_id,
            defaults=validated_data
        )

        if not created:
            for field, value in validated_data.items():
                setattr(obj, field, value)

        self.apply_toggle_logic(obj, activity_type)

        obj.activity_type = activity_type
        obj.save()

        return obj

    def apply_toggle_logic(self, obj, activity_type):
        if activity_type == "saved":
            obj.is_saved = True
        elif activity_type == "recent":
            obj.is_recent = True
        elif activity_type == "reservation":
            obj.is_reservation = True

        if activity_type == "saved-delete":
            obj.is_saved = False
        elif activity_type == "recent-delete":
            obj.is_recent = False
        elif activity_type == "reservation-delete":
            obj.is_reservation = False

class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id",
            "place_id",
            "latitude",
            "longitude",
            "place_name",
            "image",
            "rating",
            "directions_url",
            "phone",
            "email",
            "website",
            "price_currency",
            "activity_type",
            "is_saved",
            "is_recent",
            "is_reservation",
            "created_at",
            "updated_at",
        ]

