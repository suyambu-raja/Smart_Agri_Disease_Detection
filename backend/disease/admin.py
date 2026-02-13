from django.contrib import admin
from .models import DiseasePrediction


@admin.register(DiseasePrediction)
class DiseasePredictionAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'confidence', 'is_healthy', 'user_uid_short', 'filename', 'created_at']
    list_filter = ['is_healthy', 'disease_name', 'created_at']
    search_fields = ['disease_name', 'user_uid', 'filename']
    readonly_fields = ['user_uid', 'disease_name', 'confidence', 'is_healthy', 'raw_label', 'filename', 'created_at']
    ordering = ['-created_at']

    def user_uid_short(self, obj):
        return obj.user_uid[:12] + '...' if len(obj.user_uid) > 12 else obj.user_uid
    user_uid_short.short_description = 'User'
