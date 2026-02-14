from django.db import models

class UserProfile(models.Model):
    """
    Store user preferences locally in Django DB (SQLite/Postgres).
    Linked to Firebase UID.
    """
    uid = models.CharField(max_length=128, primary_key=True, help_text="Firebase UID")
    email = models.EmailField(blank=True, null=True)
    display_name = models.CharField(max_length=150, blank=True, default='')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    
    # Settings
    location = models.CharField(max_length=255, default='Chennai', help_text="Preferred city for weather")
    language = models.CharField(max_length=10, default='en', help_text="Preferred language code (en, ta, etc.)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email or self.uid}"
