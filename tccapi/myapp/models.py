# gymbroapi/models.py
from django.db import models

class TrainingData(models.Model):
    age = models.IntegerField()
    gender = models.IntegerField()
    training_days = models.IntegerField()
    training_duration = models.IntegerField()
    gym_experience = models.FloatField()
    is_natural = models.BooleanField()
