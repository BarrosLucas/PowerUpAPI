# gymbroapi/urls.py
from django.urls import path
from .views import TrainingPredictionView

urlpatterns = [
    path('predict/', TrainingPredictionView.as_view(), name='predict'),
]
