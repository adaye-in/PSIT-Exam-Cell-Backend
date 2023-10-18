from rest_framework import serializers

from .models import SeatingPlanModel, RoomSeatingModel


class SeatingPlanSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(required=False)
    marked = serializers.BooleanField(required=False)
    isDetained = serializers.BooleanField(required=False)

    class Meta:
        model = SeatingPlanModel
        fields = '__all__'


class RoomSeatingSerializer(serializers.ModelSerializer):
    seating_map = serializers.JSONField(required=False)
    marked = serializers.BooleanField(required=False)

    class Meta:
        model = RoomSeatingModel
        fields = '__all__'


class RoomSeatingSerializerResponse(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        sm = kwargs.pop('sm', 0)
        super(RoomSeatingSerializerResponse, self).__init__(*args, **kwargs)

        if sm == 0:
            exclude_fields = ['seating_map', 'user']
        else:
            exclude_fields = ['user']

        for field_name in exclude_fields:
            self.fields.pop(field_name)

    class Meta:
        model = RoomSeatingModel
        fields = '__all__'


class SessionStudentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id')
    name = serializers.CharField(source='student_name')
    roll_number = serializers.IntegerField(source='student_rn')

    class Meta:
        model = SeatingPlanModel
        fields = ['student_id', 'name', 'roll_number', 'isDetained']
