from rest_framework import serializers
from user.models import Users
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import os 

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['id', 'full_name', 'email', 'phone', 'password', 'confirm_password', 'image']
        read_only_fields = ['image']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')

        user = Users.objects.create_user(
            full_name=validated_data.get('full_name', ''),
            username=validated_data['email'], 
            email=validated_data['email'],
            password=password,
        )
        return user 
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['phone'] = user.phone
        token['image'] = user.image.url if user.image else ""

        return token
    
class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'full_name', 'email', 'phone', 'image']
    
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['full_name', 'email', 'phone', 'image'] 

    def update(self, instance, validated_data):
        if 'full_name' in validated_data and validated_data['full_name']:
            instance.full_name = validated_data['full_name']

        if 'email' in validated_data and validated_data['email']:
            new_email = validated_data['email']
            if new_email != instance.email:
                instance.email = new_email
                instance.username = new_email  

        if 'phone' in validated_data and validated_data['phone']:
            instance.phone = validated_data['phone']

        new_image = validated_data.get('image', None)
        if new_image and new_image != instance.image:
            if instance.image and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
            instance.image = new_image

        instance.save()
        return instance
    
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data




