import json
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from utility.constants import MESSAGES
from utility.response import ApiResponse


def get_serielizer_error(serializer, with_key=False):
    """handle serializer error"""
    msg_list = []
    try:
        mydict = serializer.errors
        for key in sorted(mydict.keys()):
            msg = ""

            if with_key:
                msg = f"{key} : "

            msg += str(mydict.get(key)[0])

            msg_list.append(msg)
    except Exception:
        msg_list = ["Invalid format"]
    return msg_list


def create_or_update_serializer(serializer_class, data, savepoint=None, instance=None):
    if instance:
        serializer = serializer_class(instance, data=data, partial=True)
    else:
        serializer = serializer_class(data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.instance, None

    if savepoint:
        transaction.savepoint_rollback(savepoint)

    return None, get_serielizer_error(serializer, with_key=True)


def parse_request(request: str) -> dict:
    """ load the json string request of the base class APIs """
    try:
        req_data = json.loads(request)
    except (TypeError, ValueError):
        raise ValidationError(MESSAGES["invalid_json"])

    if not isinstance(req_data, dict):
        raise ValidationError(MESSAGES["invalid_json"])
    return req_data


def call_api(self, api, req_data=None, message="Ok", code=200, **kwargs):
    """ call the base class API with a json string and return the ApiResponse """
    if req_data is not None or kwargs:
        req_data = {**(req_data if isinstance(req_data, dict) else {}), **kwargs}

    try:
        resp = api() if req_data is None else api(json.dumps(req_data))
    except NotFound as e:
        return ApiResponse.response_not_found(self, message=str(e.detail))
    except ValidationError as e:
        return ApiResponse.response_bad_request(self, message=e.detail)

    return ApiResponse.response_ok(self, message=message, code=code, data=json.loads(resp) if resp else {})
