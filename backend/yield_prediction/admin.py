from django.contrib import admin
from .models import YieldPrediction


@admin.register(YieldPrediction)
class YieldPredictionAdmin(admin.ModelAdmin):
    list_display = ['crop', 'district', 'predicted_yield', 'unit', 'risk_level', 'user_uid_short', 'created_at']
    list_filter = ['crop', 'district', 'risk_level', 'created_at']
    search_fields = ['crop', 'district', 'user_uid', 'soil_type']
    readonly_fields = ['user_uid', 'district', 'soil_type', 'crop', 'rainfall', 'temperature',
                       'predicted_yield', 'unit', 'risk_level', 'created_at']
    ordering = ['-created_at']

    def user_uid_short(self, obj):
        return obj.user_uid[:12] + '...' if len(obj.user_uid) > 12 else obj.user_uid
    user_uid_short.short_description = 'User'
