from rest_framework import serializers

from adminsession.models import SessionModel


class SessionModelSerializer(serializers.ModelSerializer):
    report_link = serializers.CharField(required=False)

    class Meta:
        model = SessionModel
        fields = '__all__'


class SessionModelSerializerResponse(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='id')

    class Meta:
        model = SessionModel
        fields = ['session_id', 'session_name', 'created_on', 'report_link']
