from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json

response_list = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": [
        {
            "name": "Backend",
            "description": "Backend team",
            "creation_time": "2026-10-25T09:00:00+00:00",
            "admin": "1"
        }
    ]
}

response_get = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": {
        "name": "Backend",
        "description": "Backend team",
        "creation_time": "2026-10-25T09:00:00+00:00",
        "admin": "1"
    }
}

response_post = {
    "message": ["Team created successfully."],
    "code": 201,
    "success": True,
    "data": {"id": "1"}
}

response_update = {
    "message": ["Team updated successfully."],
    "code": 200,
    "success": True,
    "data": {}
}

response_users = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": [
        {
            "id": "1",
            "name": "santosh",
            "display_name": "Santosh Shinde"
        }
    ]
}

response_bad_request = {
    "message": ["name : team with this name already exists."],
    "code": 400,
    "success": False,
    "data": {}
}

response_not_found = {
    "message": ["Team not found."],
    "code": 404,
    "success": False,
    "data": {}
}

team_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
        "description": openapi.Schema(type=openapi.TYPE_STRING, max_length=128),
        "admin": openapi.Schema(type=openapi.TYPE_STRING, description="id of a user"),
    },
)

users_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["users"],
    properties={
        "users": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
    },
)

swagger_auto_schema_list = swagger_auto_schema(
    responses={
        '200': json.dumps(response_list),
    },

    operation_id='list teams',
    operation_description='API to list all teams',
)

swagger_auto_schema_post = swagger_auto_schema(
    request_body=team_request_body,
    responses={
        '201': json.dumps(response_post),
        '400': json.dumps(response_bad_request),
    },

    operation_id='create team',
    operation_description='API to create team \n \n request :: {"name": "Backend", "description": "Backend team", "admin": "1"}',
)

swagger_auto_schema_update = swagger_auto_schema(
    request_body=team_request_body,
    responses={
        '200': json.dumps(response_update),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='update team',
    operation_description='API to update team \n \n request :: {"name": "Backend", "description": "Backend team", "admin": "1"}',
)

swagger_auto_schema_users = swagger_auto_schema(
    responses={
        '200': json.dumps(response_users),
        '404': json.dumps(response_not_found),
    },

    operation_id='list team users',
    operation_description='API to list users of a team',
)

swagger_auto_schema_add_users = swagger_auto_schema(
    request_body=users_request_body,
    responses={
        '200': json.dumps(response_update),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='add users to team',
    operation_description='API to add users to team, max 50 users in a team \n \n request :: {"users": ["1", "2"]}',
)

swagger_auto_schema_remove_users = swagger_auto_schema(
    request_body=users_request_body,
    responses={
        '200': json.dumps(response_update),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='remove users from team',
    operation_description='API to remove users from team \n \n request :: {"users": ["1", "2"]}',
)

swagger_auto_schema = swagger_auto_schema(
    responses={
        '200': json.dumps(response_get),
        '404': json.dumps(response_not_found),
    },

    operation_id='describe team',
    operation_description='API to fetch team',
)
