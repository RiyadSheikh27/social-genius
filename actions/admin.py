from django.contrib import admin
from actions.models import Activity
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Activity)
class ActivityemAdmin(ModelAdmin):
    list_display = [field.name for field in Activity._meta.fields if field.name not in ['activity_type',  'is_recent', 'is_saved', 'is_reservation', 'updated_at']]

    search_fields = ('id', 'user__email', 'user__full_name',)
    exclude = ('is_saved', 'is_reservation', 'is_recent') 
    list_display_links = ('id', 'user')
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_saved='True')
    def has_add_permission(self, request):
        return False
    
