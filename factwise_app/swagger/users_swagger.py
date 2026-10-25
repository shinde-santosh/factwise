from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json

response_list = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": [
        {
            "name": "santosh",
            "display_name": "Santosh Shinde",
            "creation_time": "2026-10-25T09:00:00+00:00"
        }
    ]
}

response_get = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": {
        "name": "santosh",
        "display_name": "Santosh Shinde",
        "creation_time": "2026-10-25T09:00:00+00:00"
    }
}

response_post = {
    "message": ["User created successfully."],
    "code": 201,
    "success": True,
    "data": {"id": "1"}
}

response_update = {
    "message": ["User updated successfully."],
    "code": 200,
    "success": True,
    "data": {}
}

response_teams = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": [
        {
            "name": "Backend",
            "description": "Backend team",
            "creation_time": "2026-10-25T09:00:00+00:00"
        }
    ]
}

response_bad_request = {
    "message": ["name : user with this name already exists."],
    "code": 400,
    "success": False,
    "data": {}
}

response_not_found = {
    "message": ["User not found."],
    "code": 404,
    "success": False,
    "data": {}
}

swagger_auto_schema_list = swagger_auto_schema(
    responses={
        '200': json.dumps(response_list),
    },

    operation_id='list users',
    operation_description='API to list all users',
)

swagger_auto_schema_post = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "display_name"],
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
            "display_name": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
        },
    ),
    responses={
        '201': json.dumps(response_post),
        '400': json.dumps(response_bad_request),
    },

    operation_id='create user',
    operation_description='API to create user \n \n request :: {"name": "santosh", "display_name": "Santosh Shinde"}',
)

swagger_auto_schema_update = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
            "display_name": openapi.Schema(type=openapi.TYPE_STRING, max_length=128),
        },
    ),
    responses={
        '200': json.dumps(response_update),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='update user',
    operation_description='API to update user, user name cannot be updated \n \n request :: {"display_name": "Santosh S"}',
)

swagger_auto_schema_teams = swagger_auto_schema(
    responses={
        '200': json.dumps(response_teams),
        '404': json.dumps(response_not_found),
    },

    operation_id='user teams',
    operation_description='API to list teams of a user',
)

swagger_auto_schema = swagger_auto_schema(
    responses={
        '200': json.dumps(response_get),
        '404': json.dumps(response_not_found),
    },

    operation_id='describe user',
    operation_description='API to fetch user',
)
