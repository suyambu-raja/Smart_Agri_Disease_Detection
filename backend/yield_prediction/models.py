"""
Yield Prediction – Django Models
==================================
Stores yield prediction history in Django's SQLite database.
"""

from django.db import models


class YieldPrediction(models.Model):
    """A single yield prediction result."""

    # Firebase UID of the user who made the prediction
    user_uid = models.CharField(max_length=128, db_index=True)

    # Input parameters
    district = models.CharField(max_length=100)
    soil_type = models.CharField(max_length=100)
    crop = models.CharField(max_length=100)
    rainfall = models.FloatField()
    temperature = models.FloatField()

    # Prediction results
    predicted_yield = models.FloatField()
    unit = models.CharField(max_length=20, default='kg/acre')
    risk_level = models.CharField(max_length=20, default='Low')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Yield Prediction'
        verbose_name_plural = 'Yield Predictions'

    def __str__(self):
        return f"{self.crop} in {self.district} → {self.predicted_yield} {self.unit}"
