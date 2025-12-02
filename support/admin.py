from django.contrib import admin
from support.models import *
# Register your models here.

@admin.register(SupportProblem)
class SupportProblemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Support._meta.fields if field.name not in ['type', 'status', 'updated_at', 'report', 'feedback']]
    search_fields = ('id', 'support_email', 'user__full_name',)
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type='PROBLEM')
    def has_add_permission(self, request):
        return False


@admin.register(SupportReport)
class SupportReportAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Support._meta.fields if field.name not in ['type', 'status', 'updated_at', 'problem', 'feedback']]
    search_fields = ('id', 'support_email', 'user__full_name',)
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type='REPORT')
    def has_add_permission(self, request):
        return False


@admin.register(SupportFeedback)
class SupportFeedbackAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Support._meta.fields if field.name not in ['type', 'status', 'updated_at', 'problem', 'report', 'url']]
    search_fields = ('id', 'support_email', 'user__full_name',)
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(type='FEEDBACK')
    def has_add_permission(self, request):
        return False












