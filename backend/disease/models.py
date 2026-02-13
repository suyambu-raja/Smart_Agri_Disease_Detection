"""
Disease – Django Models
========================
Stores disease detection history in Django's SQLite database.
"""

from django.db import models


class DiseasePrediction(models.Model):
    """A single disease detection result."""

    # Firebase UID of the user who made the prediction
    user_uid = models.CharField(max_length=128, db_index=True)

    # Prediction results
    disease_name = models.CharField(max_length=255)
    confidence = models.FloatField()
    is_healthy = models.BooleanField(default=False)
    raw_label = models.CharField(max_length=255, blank=True, default='')

    # Original file info
    image = models.ImageField(upload_to='disease_images/', blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, default='')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Disease Prediction'
        verbose_name_plural = 'Disease Predictions'

    def __str__(self):
        return f"{self.disease_name} ({self.confidence}%) – {self.user_uid[:8]}..."
