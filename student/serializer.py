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


class StudentListSerializerSeatingPlan(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    branch = serializers.IntegerField(source='branch.id')
    section = serializers.IntegerField(source='section.id')
    student_id = serializers.IntegerField(source='id')
    student_rn = serializers.IntegerField(source='roll_number')
    student_name = serializers.CharField(source='name')
    branch_name = serializers.CharField(source='branch.branch_name')
    section_name = serializers.CharField(source='section.section_name')

    class Meta:
        model = StudentModel
        fields = [
            'user',
            'section',
            'branch',
            'student_id',
            'student_rn',
            'student_name',
            'branch_name',
            'section_name',
        ]
