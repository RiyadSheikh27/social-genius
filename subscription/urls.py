from django.urls import path
from subscription.views import *

urlpatterns = [
    path('list/', all_subscription_list, name='all_subscription_list'),

    path('user/current-active-plan/', user_current_active_plan, name='user_current_active_plan'),

    path('checkout/', CreateStripeCheckoutSession.as_view(), name='create_checkout_session'), # api/v1/subscription/
    path('webhook/', stripe_webhook, name='stripe_webhook'),

]