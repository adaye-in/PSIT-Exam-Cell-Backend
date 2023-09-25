from rest_framework import serializers

from .models import StudentModel


class StudentModelSerializerResponse(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='id')

    class Meta:
        model = StudentModel
        fields = ['student_id', 'name', 'roll_number']


class StudentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentModel
        fields = '__all__'
