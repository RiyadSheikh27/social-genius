from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from support.serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage 

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def help_and_support(request):
    user = request.user
    serializer = SupportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    support_email = serializer.validated_data.get('support_email')
    report_type = serializer.validated_data.get('type')
    problem = serializer.validated_data.get('problem')
    report = serializer.validated_data.get('report')
    feedback = serializer.validated_data.get('feedback')
    url = serializer.validated_data.get('url')

    description = problem or report or feedback or 'No description provided.'

    message = f"Type: {report_type}\nFrom: {support_email}\n\nDescription:\n{description}\n"
    if url:
        message += f"\nRelated URL: {url}"

    subject = f"[{report_type}] Help & Support Request from {support_email}"

    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[support_email], 
        )

        email.send(fail_silently=False)
        serializer.save(user=user)
        return Response({
            'status': 'success',
            'message': f'{report_type} sent successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print('Email sending error:', e)
        return Response({
            'status': 'error',
            'message': 'Failed to send email.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






