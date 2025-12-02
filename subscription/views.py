from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from subscription.models import *
from subscription.serializers import *
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from user.models import Users

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_subscription_list(request):
    plans = SubscriptionPlan.objects.filter(status=True)
    serializer = SubscriptionPlanSerializer(instance=plans, many=True)

    return Response({
        'status': 'success',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_current_active_plan(request):
    user = request.user
    
    active_sub = UserSubscription.objects.filter(user=user, is_active=True).last()

    if active_sub and active_sub.is_plan_active():
        return Response({
            'status': 'success',
            'plan': 'paid',
            'data': UserSubscriptionSerializer(active_sub).data,
            'plan_details': SubscriptionPlanSerializer(active_sub.plan).data
        }, status=200)

    # Return FREE plan
    free_plan = SubscriptionPlan.objects.filter(status=True, name='FREE').first()

    return Response({
        'status': 'success',
        'plan': 'free',
        'plan_details': SubscriptionPlanSerializer(free_plan).data
    }, status=200)

class CreateStripeCheckoutSession(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            print('stripe.api_key : ', stripe.api_key)
            plan_id = request.data.get("plan_id")
            if not plan_id or plan_id=='1':
                return Response({'plan_id': 'plan_id is required. Avoid ID 1'}, status=status.HTTP_400_BAD_REQUEST)
            
            subscription = get_object_or_404(SubscriptionPlan, id=plan_id)
            price = subscription.price
            print('price : ', price)

            # create Stripe Checkout Session for paid plans
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency':"eur",
                        'unit_amount': int(price * 100),
                        'product_data': {
                            'name': f"{subscription.name} Plan Subscription",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.FRONTEND_URL + '/success',
                cancel_url=settings.FRONTEND_URL + '/cancel',
                metadata={
                    "user_id": request.user.id,
                    "sub_id": subscription.id
                }
            )

            return Response({
                'sessionId': checkout_session.id,
                'checkout_url': checkout_session.url
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def stripe_webhook(request):
    print('webhook call')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'error': 'Invalid payload or signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        sub_id = session['metadata']['sub_id']
        transaction_id = session.get('payment_intent')

        user = get_object_or_404(Users, id=user_id)
        subscription = get_object_or_404(SubscriptionPlan, id=sub_id)

        UserSubscription.objects.filter(user=user, is_active=True).update(is_active=False)
       
        UserSubscription.objects.create(
            user=user,
            plan=subscription,
            stripe_subscription_id=transaction_id,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=subscription.duration_days),
        )

    return JsonResponse({'status': 'success'}, status=200)








