from django.db import models

class WeatherLog(models.Model):
    city = models.CharField(max_length=100, default='Chennai')
    temperature = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.IntegerField(null=True, blank=True)
    wind_speed = models.FloatField()
    description = models.CharField(max_length=100)
    rainfall = models.FloatField(default=0.0)
    clouds = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.city} - {self.temperature}°C ({self.timestamp})"
