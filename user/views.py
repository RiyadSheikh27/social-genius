from django.shortcuts import render, HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from user.models import OTP
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from user.serializers import *
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework_simplejwt.views import TokenObtainPairView 
# from django.http import HttpResponse

# Create your views here.
@api_view(['POST'])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({
            'status': 'error',
            'email': 'email filed required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    otp = random.randint(100000, 999999)
    subject = 'Create Account OTP'
    message = f'Your OTP code is {otp}. It is valid for 5 minutes.'

    try:
        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        otp_obj, _ = OTP.objects.update_or_create(email=email , defaults={'otp':otp})

        return Response({
            'status': 'succes',
            'message': f'OTP successfully sent to {email}'
        })

    except Exception as e:
        print('error : ', e)
        return Response({
            'status': 'error',
            "message": "Failed to send OTP email."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def otp_code_verified(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({
            'status': 'error',
            'message': "'email' and 'otp' required"
        }, status=status.HTTP_400_BAD_REQUEST)
     
    if OTP.objects.filter(email=email, otp=otp).exists():
        otp_obj = OTP.objects.get(email=email)
        otp_value = otp_obj.otp

        if otp_obj.otp_expired_at > timezone.now():
            if otp == otp_value:
                otp_obj.otp = ""
                otp_obj.save()
                return Response({
                    'status': 'success',
                    'message': 'OTP verified'
                }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'OTP Expired'
        })
    return Response({
        'status': 'error',
        'message': "'email' or 'otp' wrong"
    })

@api_view(['POST'])     
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()
    refresh = RefreshToken.for_user(user)

    return Response({
        'status': 'success',
        'user': serializer.data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
def social_signup_signup(request):
    email = request.data.get('email')
    full_name = request.data.get('full_name')
    auth_provider = request.data.get('auth_provider')

    if not email or not full_name or not auth_provider:
        return Response({
            "email": "This field is required." ,
            "full_name": "This field is required." ,
            "auth_provider": "This field is required." ,
        }, status=400)

    user, created = Users.objects.get_or_create(
        email=email, 
        defaults={'username': email, 'email':email, 'full_name': full_name}
    )

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    token = {
        'refresh': str(refresh),
        'access': str(access_token),
    }

    user_details = {
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'phone': user.phone,
        'image': user.image.url if user.image else None
    }

    return Response({
        'message': 'Successfully authenticated.',
        'user': user_details,
        'token': token,
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  

        token_data = serializer.validated_data

        return Response({
            "status": "success",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "image": user.image.url if user.image else None
            },
            "refresh": token_data["refresh"],
            "access": token_data["access"],
        }, status=status.HTTP_200_OK)
    

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserDataSerializer(user)
        return Response({
            'status': 'success',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    if request.method == 'PATCH':
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'status': 'success',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changed_password(request):
    user = request.user
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not user.check_password(serializer.validated_data['current_password']):
        return Response(
            {"error": "Your current password is not correct."},
            status=status.HTTP_400_BAD_REQUEST
        )
     
    new_password = serializer.validated_data['new_password']
    
    user.set_password(new_password)
    user.save()

    return Response({
        "status": "success",
        "message": "Password changed successfully."
        },status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({
            'status': 'error',
            'email': 'email filed required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not Users.objects.filter(email=email).exists():
        return Response({
            'status': 'error',
            'email': 'No account found with this email.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    otp = random.randint(100000, 999999)
    subject = 'Forgot Password OTP'
    message = f'Your OTP code is {otp}. It is valid for 5 minutes.'

    try:
        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        otp_obj, _ = OTP.objects.update_or_create(email=email , defaults={'otp':otp})

        return Response({
            'status': 'succes',
            'message': f'OTP successfully sent to {email}'
        })

    except Exception as e:
        print('error : ', e)
        return Response({
            'status': 'error',
            "message": "Failed to send OTP email."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_new_password(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not Users.objects.filter(email=serializer.validated_data['email']).exists():  
        return Response({"error": "No account found with this email."}, status=status.HTTP_404_NOT_FOUND)
    
    user = Users.objects.get(email=serializer.validated_data['email'])
    user.set_password(serializer.validated_data['password'])
    user.save()

    return Response({
        "status": "success",
        "message": "Password has been reset successfully."
        }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    user = request.user
    print('id : ', user.id , '||type : ', type(user), '||user : ', user)
 
    OTP.objects.filter(email=user.email).delete()

    user.delete()

    return Response({
        'status': 'success',
        'message': 'Account Delete Successfull'
    }, status=status.HTTP_200_OK)


