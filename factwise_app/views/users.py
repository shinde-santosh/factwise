import json
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import GenericViewSet

""" utility """
from utility.constants import CREATE_DISPLAY_NAME_MAX, MESSAGES
from utility.response import ApiResponse
from utility.utils import call_api, create_or_update_serializer, parse_request

""" model imports """
from ..models import User

''' serializers '''
from ..serializers.users_serializer import UsersSerializer

""" base class """
from .user_base import UserBase

"""swagger"""
from ..swagger.users_swagger import (swagger_auto_schema_list, swagger_auto_schema_post, swagger_auto_schema,
                                     swagger_auto_schema_update, swagger_auto_schema_teams)


class UsersView(UserBase, GenericViewSet, ApiResponse):
    serializer_class = UsersSerializer
    singular_name = "User"
    model_class = User.objects

    def get_object(self, pk):
        try:
            return self.model_class.get(pk=pk)
        except Exception:
            raise NotFound(self.singular_name + MESSAGES["not_found"])

    # create a user
    def create_user(self, request: str) -> str:
        req_data = parse_request(request)

        data = {"name": req_data.get("name"), "display_name": req_data.get("display_name")}
        data = {key: value for key, value in data.items() if value is not None}

        # display name can be max 64 characters on create, the model allows 128 for update
        if isinstance(data.get("display_name"), str) and len(data["display_name"].strip()) > CREATE_DISPLAY_NAME_MAX:
            raise ValidationError(MESSAGES["display_name_max"])

        instance, error = create_or_update_serializer(self.serializer_class, data)
        if error:
            raise ValidationError(error)

        return json.dumps({"id": str(instance.id)})

    # list all users
    def list_users(self) -> str:
        return json.dumps([self.transform_single(instance) for instance in self.model_class.order_by("id")])

    # describe user
    def describe_user(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        return json.dumps(self.transform_single(instance))

    # update user
    def update_user(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        user_data = req_data.get("user")
        if not isinstance(user_data, dict):
            raise ValidationError(MESSAGES["invalid_json"])

        if "name" in user_data and user_data["name"] != instance.name:
            raise ValidationError(MESSAGES["name_cannot_update"])

        data = {"display_name": user_data.get("display_name")}
        data = {key: value for key, value in data.items() if value is not None}

        _, error = create_or_update_serializer(self.serializer_class, data, instance=instance)
        if error:
            raise ValidationError(error)

        return json.dumps({})

    # list teams of a user
    def get_user_teams(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        return json.dumps([
            {
                "name": team.name,
                "description": team.description,
                "creation_time": team.created_at.isoformat(),
            }
            for team in instance.teams.order_by("id")
        ])

    @swagger_auto_schema_list
    def list(self, request, *args, **kwargs):
        """
        :To get the all records
        """
        return call_api(self, self.list_users)

    @swagger_auto_schema_post
    def create(self, request, *args, **kwargs):
        """
        :To create the new record
        """
        return call_api(self, self.create_user, request.data, message=self.singular_name + MESSAGES["created"], code=201)

    @swagger_auto_schema
    def retrieve(self, request, *args, **kwargs):
        """
        :To get the single record
        """
        return call_api(self, self.describe_user, id=self.kwargs.get("id"))

    @swagger_auto_schema_update
    def partial_update(self, request, *args, **kwargs):
        """
        :To update the existing record
        """
        return call_api(self, self.update_user, id=self.kwargs.get("id"), user=request.data,
                        message=self.singular_name + MESSAGES["updated"])

    @swagger_auto_schema_teams
    def teams(self, request, *args, **kwargs):
        """
        :To get the teams of the user
        """
        return call_api(self, self.get_user_teams, id=self.kwargs.get("id"))

    # Generate the response
    def transform_single(self, instance):
        resp_dict = {}
        resp_dict['name'] = instance.name
        resp_dict['display_name'] = instance.display_name
        resp_dict['creation_time'] = instance.created_at.isoformat()

        return resp_dict
