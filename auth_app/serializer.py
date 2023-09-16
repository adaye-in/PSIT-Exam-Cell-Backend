from datetime import datetime

import bcrypt
from rest_framework import serializers

from .models import AdminModel


class AdminModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminModel
        fields = ('email_address', 'password')

    def create(self, validated_data):
        validated_data['created_at'] = datetime.now()
        validated_data["password"] = bcrypt.hashpw(validated_data["password"].encode('utf-8'), bcrypt.gensalt()).decode(
            'utf-8')
        instance = AdminModel(**validated_data)
        instance.save()
        return instance
