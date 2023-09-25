from rest_framework import serializers

from .models import *


class BranchModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchModel
        fields = '__all__'


class BranchModelSerializerResponse(serializers.ModelSerializer):
    branch_id = serializers.IntegerField(source='id')

    class Meta:
        model = BranchModel
        fields = ['branch_id', 'duration_of_course_year', 'branch_name', 'created_on']


class SectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionModel
        fields = '__all__'


class SectionModelSerializerResponse(serializers.ModelSerializer):
    section_id = serializers.IntegerField(source='id')
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = SectionModel
        fields = ['section_id', 'branch_id', 'section_name', 'present_year', 'created_on', 'branch_name']


class RoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomModel
        fields = '__all__'


class RoomModelSerializerResponse(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source='id')

    class Meta:
        model = RoomModel
        fields = ['room_id', 'room_number', 'room_rows', 'room_columns', 'created_on', 'room_breakout']
