from django.urls import path
from .views import TextToSpeechView

urlpatterns = [
    path('generate/', TextToSpeechView.as_view(), name='tts-generate'),
]
