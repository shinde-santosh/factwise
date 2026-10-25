import json
import os
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.viewsets import GenericViewSet

""" utility """
from utility.constants import MESSAGES, STATUS_CLOSED, STATUS_COMPLETE, STATUS_OPEN, TASK_STATUSES
from utility.response import ApiResponse
from utility.utils import call_api, create_or_update_serializer, parse_request

""" model imports """
from ..models import Board, Task, Team

''' serializers '''
from ..serializers.boards_serializer import BoardsSerializer
from ..serializers.tasks_serializer import TasksSerializer

""" base class """
from .project_board_base import ProjectBoardBase

"""swagger"""
from ..swagger.project_board_swagger import (swagger_auto_schema_list, swagger_auto_schema_post,
                                             swagger_auto_schema_close, swagger_auto_schema_export,
                                             swagger_auto_schema_task_post, swagger_auto_schema_task_update)


class ProjectBoardView(ProjectBoardBase, GenericViewSet, ApiResponse):
    serializer_class = BoardsSerializer
    singular_name = "Board"
    model_class = Board.objects

    def get_object(self, pk, model_class=None, singular_name=None):
        try:
            return (model_class or self.model_class).get(pk=pk)
        except Exception:
            raise NotFound((singular_name or self.singular_name) + MESSAGES["not_found"])

    # create a board
    def create_board(self, request: str):
        req_data = parse_request(request)
        team = self.get_object(req_data.get("team_id"), Team.objects, "Team")

        data = {
            "name": req_data.get("name"),
            "description": req_data.get("description"),
            "team": team.id,
            "created_at": req_data.get("creation_time"),
        }
        data = {key: value for key, value in data.items() if value is not None}

        if team.boards.filter(name=data.get("name")).exists():
            raise ValidationError(self.singular_name + MESSAGES["already_exists"])

        instance, error = create_or_update_serializer(self.serializer_class, data)
        if error:
            raise ValidationError(error)

        return json.dumps({"id": str(instance.id)})

    # close a board
    def close_board(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))

        if instance.status == STATUS_CLOSED:
            raise ValidationError(MESSAGES["board_closed"])

        if instance.tasks.exclude(status=STATUS_COMPLETE).exists():
            raise ValidationError(MESSAGES["tasks_not_complete"])

        instance.status = STATUS_CLOSED
        instance.end_time = timezone.now()
        instance.save()

        return json.dumps({})

    # add task to board
    def add_task(self, request: str) -> str:
        req_data = parse_request(request)
        board = self.get_object(req_data.get("board_id"))

        if board.status != STATUS_OPEN:
            raise ValidationError(MESSAGES["board_not_open"])

        data = {
            "title": req_data.get("title"),
            "description": req_data.get("description"),
            "user": req_data.get("user_id"),
            "board": board.id,
            "created_at": req_data.get("creation_time"),
        }
        data = {key: value for key, value in data.items() if value is not None}

        if board.tasks.filter(title=data.get("title")).exists():
            raise ValidationError("Task" + MESSAGES["already_exists"])

        instance, error = create_or_update_serializer(TasksSerializer, data)
        if error:
            raise ValidationError(error)

        return json.dumps({"id": str(instance.id)})

    # update the status of a task
    def update_task_status(self, request: str):
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"), Task.objects, "Task")

        if req_data.get("status") not in TASK_STATUSES:
            raise ValidationError(MESSAGES["invalid_status"])

        instance.status = req_data["status"]
        instance.save()

        return json.dumps({})

    # list all open boards for a team
    def list_boards(self, request: str) -> str:
        req_data = parse_request(request)
        team = self.get_object(req_data.get("id"), Team.objects, "Team")

        return json.dumps([
            {"id": str(board.id), "name": board.name}
            for board in team.boards.filter(status=STATUS_OPEN).order_by("id")
        ])

    def export_board(self, request: str) -> str:
        req_data = parse_request(request)
        instance = self.get_object(req_data.get("id"))
        tasks = instance.tasks.select_related("user").order_by("id")

        line = "=" * 70
        completed = len([task for task in tasks if task.status == STATUS_COMPLETE])
        lines = [
            line,
            f" BOARD       : {instance.name}  [{instance.status}]",
            f" Team        : {instance.team.name}",
            f" Description : {instance.description or '-'}",
            f" Created     : {instance.created_at:%d %b %Y %H:%M} UTC",
            f" Closed      : {f'{instance.end_time:%d %b %Y %H:%M} UTC' if instance.end_time else '-'}",
            f" Progress    : {completed}/{len(tasks)} tasks complete",
            line,
        ]

        for status in TASK_STATUSES:
            status_tasks = [task for task in tasks if task.status == status]
            lines += ["", f" {status} ({len(status_tasks)})", "-" * 70]
            lines += [
                f" #{task.id} {task.title}\n    Assignee : {task.user.display_name} ({task.user.name})"
                f"\n    Created  : {task.created_at:%d %b %Y %H:%M} UTC"
                + (f"\n    Notes    : {task.description}" if task.description else "")
                for task in status_tasks
            ] or [" No tasks"]

        os.makedirs(settings.OUT_DIR, exist_ok=True)
        out_file = f"board_{instance.id}.txt"
        with open(os.path.join(settings.OUT_DIR, out_file), "w") as file:
            file.write("\n".join(lines) + "\n")

        return json.dumps({"out_file": out_file})

    @swagger_auto_schema_list
    def list(self, request, *args, **kwargs):
        """
        :To get the all open boards of a team
        """
        return call_api(self, self.list_boards, id=self.kwargs.get("id"))

    @swagger_auto_schema_post
    def create(self, request, *args, **kwargs):
        """
        :To create the new record
        """
        return call_api(self, self.create_board, request.data, message=self.singular_name + MESSAGES["created"], code=201)

    @swagger_auto_schema_close
    def close(self, request, *args, **kwargs):
        """
        :To close the board
        """
        return call_api(self, self.close_board, id=self.kwargs.get("id"), message="Board closed successfully.")

    @swagger_auto_schema_export
    def export(self, request, *args, **kwargs):
        """
        :To export the board
        """
        return call_api(self, self.export_board, id=self.kwargs.get("id"))

    @swagger_auto_schema_task_post
    def create_task(self, request, *args, **kwargs):
        """
        :To add the task to board
        """
        return call_api(self, self.add_task, request.data, message="Task" + MESSAGES["created"], code=201)

    @swagger_auto_schema_task_update
    def update_task(self, request, *args, **kwargs):
        """
        :To update the status of task
        """
        return call_api(self, self.update_task_status, request.data, id=self.kwargs.get("id"),
                        message="Task" + MESSAGES["updated"])
