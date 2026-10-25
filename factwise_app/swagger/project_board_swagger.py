from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import json

response_list = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": [
        {
            "id": "1",
            "name": "Sprint 1"
        }
    ]
}

response_post = {
    "message": ["Board created successfully."],
    "code": 201,
    "success": True,
    "data": {"id": "1"}
}

response_close = {
    "message": ["Board closed successfully."],
    "code": 200,
    "success": True,
    "data": {}
}

response_export = {
    "message": ["Ok"],
    "code": 200,
    "success": True,
    "data": {"out_file": "board_1.txt"}
}

response_task_post = {
    "message": ["Task created successfully."],
    "code": 201,
    "success": True,
    "data": {"id": "1"}
}

response_task_update = {
    "message": ["Task updated successfully."],
    "code": 200,
    "success": True,
    "data": {}
}

response_bad_request = {
    "message": ["Board can be closed only when all tasks are COMPLETE."],
    "code": 400,
    "success": False,
    "data": {}
}

response_not_found = {
    "message": ["Board not found."],
    "code": 404,
    "success": False,
    "data": {}
}

swagger_auto_schema_list = swagger_auto_schema(
    responses={
        '200': json.dumps(response_list),
        '404': json.dumps(response_not_found),
    },

    operation_id='list boards',
    operation_description='API to list all open boards of a team',
)

swagger_auto_schema_post = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "team_id"],
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
            "description": openapi.Schema(type=openapi.TYPE_STRING, max_length=128),
            "team_id": openapi.Schema(type=openapi.TYPE_STRING),
            "creation_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        },
    ),
    responses={
        '201': json.dumps(response_post),
        '400': json.dumps(response_bad_request),
    },

    operation_id='create board',
    operation_description='API to create board \n \n request :: {"name": "Sprint 1", "description": "First sprint", "team_id": "1", "creation_time": "2026-10-25T09:00:00Z"}',
)

swagger_auto_schema_close = swagger_auto_schema(
    responses={
        '200': json.dumps(response_close),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='close board',
    operation_description='API to close board, all tasks of the board must be COMPLETE',
)

swagger_auto_schema_export = swagger_auto_schema(
    responses={
        '200': json.dumps(response_export),
        '404': json.dumps(response_not_found),
    },

    operation_id='export board',
    operation_description='API to export board as a txt file in the out folder',
)

swagger_auto_schema_task_post = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["title", "user_id", "board_id"],
        properties={
            "title": openapi.Schema(type=openapi.TYPE_STRING, max_length=64),
            "description": openapi.Schema(type=openapi.TYPE_STRING, max_length=128),
            "user_id": openapi.Schema(type=openapi.TYPE_STRING),
            "board_id": openapi.Schema(type=openapi.TYPE_STRING),
            "creation_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        },
    ),
    responses={
        '201': json.dumps(response_task_post),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='add task',
    operation_description='API to add task to an open board \n \n request :: {"title": "Build API", "description": "Write the endpoints", "user_id": "1", "board_id": "1", "creation_time": "2026-10-25T09:00:00Z"}',
)

swagger_auto_schema_task_update = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["status"],
        properties={
            "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["OPEN", "IN_PROGRESS", "COMPLETE"]),
        },
    ),
    responses={
        '200': json.dumps(response_task_update),
        '400': json.dumps(response_bad_request),
        '404': json.dumps(response_not_found),
    },

    operation_id='update task status',
    operation_description='API to update status of a task \n \n request :: {"status": "IN_PROGRESS"}',
)
