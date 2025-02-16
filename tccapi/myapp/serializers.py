# gymbroapi/serializers.py
from rest_framework import serializers

class TrainingDataSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    gender = serializers.IntegerField()
    training_days = serializers.IntegerField()
    training_duration = serializers.IntegerField()
    gym_experience = serializers.FloatField()
    is_natural = serializers.BooleanField()
