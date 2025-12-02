from subscription.models import SubscriptionPlan, UserSubscription, UserFreeUsage
from user.models import Users
from django.utils import timezone
import calendar

def check_user_all_plan_limit(user, used_type): # user => object
    paid_plan = UserSubscription.objects.filter(user=user, is_active=True).last()
    paid_plan_has_limit = True

    if paid_plan and paid_plan.is_plan_active():
        # print('checking paid plan limit for user:', paid_plan)
        if used_type == 'place':
            paid_plan_has_limit = paid_plan.has_place_remaining()
        elif used_type == 'ai':
            paid_plan_has_limit = paid_plan.has_ai_remaining()
        elif used_type == 'weather':
            paid_plan_has_limit = paid_plan.has_weather_remaining()

        if paid_plan_has_limit:
            return True
        
        # print("Paid plan limit exceeded. Falling back to free plan...")


    free_plan = SubscriptionPlan.objects.get(name='FREE')
    # print('checking free plan limit for user:', free_plan)

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # print('Month start:', month_start)
    last_day = calendar.monthrange(now.year, now.month)[1]
    month_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    # print('Month end:', month_end)

    free_usage = UserFreeUsage.objects.filter(
        user=user,
        updated_at__gte=month_start,
        updated_at__lte=month_end
    )

    if used_type == 'place' and free_plan.place_limit is None:
        return True
    if used_type == 'ai' and free_plan.ai_limit is None:
        return True
    if used_type == 'weather' and free_plan.weather_limit is None:
        return True
    
    total_used_places_this_month = 0
    total_used_ai_this_month = 0
    total_used_weather_this_month = 0

    for uses in free_usage:
        # print('Free usage record:', uses.id)
        if uses.used_places:
            # print('  used places:', uses.used_places)
            total_used_places_this_month += uses.used_places
        if uses.used_ai:
            total_used_ai_this_month += uses.used_ai
        if uses.used_weather:
            total_used_weather_this_month += uses.used_weather

    print('Total used places in free plan this month:', total_used_places_this_month)
    print('Total used ai in free plan this month:', total_used_ai_this_month)
    print('Total used weather in free plan this month:', total_used_weather_this_month)

    if used_type == 'place' and total_used_places_this_month >= free_plan.place_limit:
        return False
    if used_type == 'ai'and total_used_ai_this_month >= free_plan.ai_limit:
        return False
    if used_type == 'weather' and total_used_weather_this_month >= free_plan.weather_limit:
        return False
            
    return True 

def check_user_paid_subscription(user, used_type): # user => object
    paid_plan = UserSubscription.objects.filter(user=user, is_active=True).last()
    paid_plan_has_limit = False

    if paid_plan and paid_plan.is_plan_active():
        # print('check_user_paid_subscription:', paid_plan)
        if used_type == 'place':
            paid_plan_has_limit = paid_plan.has_place_remaining()
        elif used_type == 'ai':
            paid_plan_has_limit = paid_plan.has_ai_remaining()
        elif used_type == 'weather':
            paid_plan_has_limit = paid_plan.has_weather_remaining()

        if paid_plan_has_limit:
            return True
        
    return False

def increase_paid_subscription_usage(user, used_type, amount=1):
    paid_plan = UserSubscription.objects.filter(user=user, is_active=True).last()
    # print('paid plan active : ', paid_plan)
    if paid_plan and paid_plan.is_plan_active():
        if used_type == 'place':
            paid_plan.used_places += amount
        elif used_type == 'ai':
            paid_plan.used_ai += amount
        elif used_type == 'weather':
            paid_plan.used_weather += amount
        paid_plan.save()

def increase_free_usage(user, used_type, amount=1):
    UserFreeUsage.objects.create(
        user=user,
        used_places=amount if used_type == 'place' else 0,
        used_ai=amount if used_type == 'ai' else 0,
        used_weather=amount if used_type == 'weather' else 0
    )




