from datetime import datetime

import jwt
from rest_framework import status
from rest_framework.response import Response

from .constants import *


# Response function
def response_fun(*args):
    if args[0] == 1:
        # args[1]['status_code'] = STATUS_OK
        return Response({'status': args[0], 'responseData': args[1], 'status_code': status.HTTP_200_OK, 'error': False})
    else:
        return Response({'status': args[0], 'error': True, 'message': args[1], 'status_code': STATUS_FAILED})


def response_fun_dict(*args):
    if args[0] == 1:
        args[1]['status_code'] = status.HTTP_200_OK
        return {'status': args[0], 'responseData': args[1], 'status_code': status.HTTP_200_OK, 'error': False}
    else:
        return {'status': args[0], 'error': True, 'message': args[1], 'status_code': STATUS_FAILED}


# Encode jwt token
def encode_token(payload):
    current_time = datetime.now().strftime("%H:%M:%S:%f")
    payload['time'] = current_time
    encoded_token = jwt.encode(payload, "key", algorithm="HS256")

    return encoded_token


# Decode jwt token
def decode_token(token):
    try:
        decoded_token = jwt.decode(token, "key", algorithms=["HS256"])
        return decoded_token

    except jwt.DecodeError:
        return response_fun(0, INVALID_TOKEN)
