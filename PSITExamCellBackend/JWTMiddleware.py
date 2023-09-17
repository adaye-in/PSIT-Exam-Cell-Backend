import jwt
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import status
from rest_framework.exceptions import APIException

from PSITExamCellBackend.utils import response_fun_dict


class AuthenticationFailedStatusOk(APIException):
    status_code = status.HTTP_200_OK
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'


def process_jwt_token(token):
    """
    Authenticate the JWT token and return the decoded payload.
    """
    try:
        decoded_token = jwt.decode(token, "key", algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailedStatusOk("Token has expired")
    except jwt.DecodeError:
        raise AuthenticationFailedStatusOk("Invalid token")
    except jwt.InvalidTokenError:
        raise AuthenticationFailedStatusOk("Token is invalid")


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the JWT token from the request headers.
        token = request.META.get('HTTP_TOKEN')
        if not token:
            raise AuthenticationFailedStatusOk(detail=response_fun_dict(0, 'Token Not Found'))
        try:
            decoded_payload = process_jwt_token(token)
        except AuthenticationFailedStatusOk as e:
            raise AuthenticationFailedStatusOk(detail=response_fun_dict(0, e))
        # Check weather the user exits in db or has been deleted . find in db
        return decoded_payload
