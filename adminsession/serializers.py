from rest_framework import serializers

from adminsession.models import SessionModel


class SessionModelSerializer(serializers.ModelSerializer):
    report_link = serializers.CharField(required=False)

    class Meta:
        model = SessionModel
        fields = '__all__'
