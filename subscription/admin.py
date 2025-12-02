from django.contrib import admin
from subscription.models import SubscriptionPlan, UserSubscription, UserFreeUsage
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = [field.name for field in SubscriptionPlan._meta.fields]

    search_fields = ('id', 'name')
    list_filter = ('status', 'duration_days', 'price')
    list_display_links = ('id', 'name')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.name.upper() == "FREE":
            return False
        return True
    
@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    list_display = [field.name for field in UserSubscription._meta.fields]

    search_fields = ('id', 'user__email', 'subscription_plan__name')
    list_filter = ('is_active', 'plan__name')
    list_display_links = ('id', 'user')

    list_per_page = 20
