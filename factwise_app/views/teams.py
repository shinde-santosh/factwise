import json
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import GenericViewSet

""" utility """
from utility.constants import MAX_TEAM_USERS, MESSAGES
from utility.response import ApiResponse
from utility.utils import call_api, create_or_update_serializer, parse_request

""" model imports """
from ..models import Team, User

''' serializers '''
from ..serializers.teams_serializer import TeamsSerializer

""" base class """
from .team_base import TeamBase

"""swagger"""
from ..swagger.teams_swagger import (swagger_auto_schema_list, swagger_auto_schema_post, swagger_auto_schema,
                                     swagger_auto_schema_update, swagger_auto_schema_users,
                                     swagger_auto_schema_add_users, swagger_auto_schema_remove_users)


class TeamsView(TeamBase, GenericViewSet, ApiResponse):
    serializer_class = TeamsSerializer
    singular_name = "Team"
    model_class = Team.objects

    def get_object(self, pk):
        try:
            return self.model_class.get(pk=pk)
        except Exception:
            raise NotFound(self.singular_name + MESSAGES["not_found"])

    def get_users(self, user_ids):
        if not isinstance(user_ids, list) or not user_ids:
            raise ValidationError(MESSAGES["invalid_users"])

        try:
            users = list(User.objects.filter(id__in=set(user_ids)))
        except (TypeError, ValueError):
            raise ValidationError(MESSAGES["invalid_users"])

        if len(users) != len(set(map(str, user_ids))):
            raise NotFound("User" + MESSAGES["not_found"])
        return users

    # create a team
    def create_team(self, request: str) -> str:
        req_data = parse_request(request)

        data = {"name": req_data.get("name"), "description": req_data.get("description"), "admin": req_data.get("admin")}
        data = {key: value for key, value in data.items() if value is not None}

        instance, error = create_or_update_serializer(self.serializer_class, data)
        if error:
            raise ValidationError(error)

        return json.dumps({"id": str(instance.id)})

    # list all teams
    def list_teams(self) -> str:
        return json.dumps([self.transform_single(instance) for instance in self.model_class.order_by("id")])

    # describe team
    def describe_team(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        return json.dumps(self.transform_single(instance))

    # update team
    def update_team(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        team_data = req_data.get("team")
        if not isinstance(team_data, dict):
            raise ValidationError(MESSAGES["invalid_json"])

        data = {"name": team_data.get("name"), "description": team_data.get("description"), "admin": team_data.get("admin")}
        data = {key: value for key, value in data.items() if value is not None}

        _, error = create_or_update_serializer(self.serializer_class, data, instance=instance)
        if error:
            raise ValidationError(error)

        return json.dumps({})

    # add users to team
    def add_users_to_team(self, request: str):
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))
        users = self.get_users(req_data.get("users"))

        team_user_ids = set(instance.users.values_list("id", flat=True)) | {user.id for user in users}
        if len(team_user_ids) > MAX_TEAM_USERS:
            raise ValidationError(MESSAGES["max_team_users"])

        instance.users.add(*users)

        return json.dumps({})

    # remove users from team
    def remove_users_from_team(self, request: str):
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))
        users = self.get_users(req_data.get("users"))

        instance.users.remove(*users)

        return json.dumps({})

    # list users of a team
    def list_team_users(self, request: str):
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        return json.dumps([
            {"id": str(user.id), "name": user.name, "display_name": user.display_name}
            for user in instance.users.order_by("id")
        ])

    @swagger_auto_schema_list
    def list(self, request, *args, **kwargs):
        """
        :To get the all records
        """
        return call_api(self, self.list_teams)

    @swagger_auto_schema_post
    def create(self, request, *args, **kwargs):
        """
        :To create the new record
        """
        return call_api(self, self.create_team, request.data, message=self.singular_name + MESSAGES["created"], code=201)

    @swagger_auto_schema
    def retrieve(self, request, *args, **kwargs):
        """
        :To get the single record
        """
        return call_api(self, self.describe_team, id=self.kwargs.get("id"))

    @swagger_auto_schema_update
    def partial_update(self, request, *args, **kwargs):
        """
        :To update the existing record
        """
        return call_api(self, self.update_team, id=self.kwargs.get("id"), team=request.data,
                        message=self.singular_name + MESSAGES["updated"])

    @swagger_auto_schema_users
    def users(self, request, *args, **kwargs):
        """
        :To get the users of the team
        """
        return call_api(self, self.list_team_users, id=self.kwargs.get("id"))

    @swagger_auto_schema_add_users
    def add_users(self, request, *args, **kwargs):
        """
        :To add users to the team
        """
        return call_api(self, self.add_users_to_team, request.data, id=self.kwargs.get("id"),
                        message=self.singular_name + MESSAGES["updated"])

    @swagger_auto_schema_remove_users
    def remove_users(self, request, *args, **kwargs):
        """
        :To remove users from the team
        """
        return call_api(self, self.remove_users_from_team, request.data, id=self.kwargs.get("id"),
                        message=self.singular_name + MESSAGES["updated"])

    # Generate the response
    def transform_single(self, instance):
        resp_dict = {}
        resp_dict['name'] = instance.name
        resp_dict['description'] = instance.description
        resp_dict['creation_time'] = instance.created_at.isoformat()
        resp_dict['admin'] = str(instance.admin_id)

        return resp_dict
