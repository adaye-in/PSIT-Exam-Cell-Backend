from rest_framework import serializers

from .models import SeatingPlanModel, RoomSeatingModel


class SeatingPlanSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(required=False)
    marked = serializers.BooleanField(required=False)

    class Meta:
        model = SeatingPlanModel
        fields = '__all__'


class RoomSeatingSerializer(serializers.ModelSerializer):
    seating_map = serializers.JSONField(required=False)
    marked = serializers.BooleanField(required=False)

    class Meta:
        model = RoomSeatingModel
        fields = '__all__'
