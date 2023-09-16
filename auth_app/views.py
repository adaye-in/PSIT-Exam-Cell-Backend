import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets
from rest_framework.decorators import action

from PSITExamCellBackend.constants import *
from PSITExamCellBackend.utils import response_fun, encode_token
from .models import *
from .serializer import AdminModelSerializer


class AdminViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        :param request:
        :return:
        """
        serializer = AdminModelSerializer(data=request.data)
        if serializer.is_valid():
            admin_instance = serializer.save()
            return response_fun(1, {
                'message': 'Admin registered successfully.'
            })
        else:
            return response_fun(0, UNPROCESSABLE_ENTITY)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Endpoint for performing login action
        :param request:
        :return jwt Token if successful:
        """
        try:
            request_data = request.data
            if request_data.get("email_address"):
                request_data["email_address"] = request_data.get("email_address").lower()
            else:
                return response_fun(0, UNPROCESSABLE_ENTITY)

            if not request_data.get("password"):
                return response_fun(0, UNPROCESSABLE_ENTITY)

            admin_obj = AdminModel.objects.get(email_address=request_data.get("email_address"))
            if not admin_obj:
                return response_fun(0, USER_NOT_EXISTS)
            stored_password = admin_obj.password.encode('utf-8')
            if not bcrypt.checkpw(request_data.get("password").encode('utf-8'), stored_password):
                return response_fun(0, INVALID_CREDENTIAL)
            payload = {
                "pk": admin_obj.id,
                "email_address": admin_obj.email_address
            }

            jwt_encoded = encode_token(payload)

            return response_fun(1, {
                "Token": jwt_encoded,
            })

        except ObjectDoesNotExist:
            return response_fun(0, USER_NOT_EXISTS)

        except Exception as e:
            print(e)
            return response_fun(0, INTERNAL_ERROR)
