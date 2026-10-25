import json
import os
import tempfile
from django.test import override_settings
from rest_framework.exceptions import NotFound, ValidationError

from utility.constants import *
from utility.test_utility import *

"""Model"""
from ..models import Board, Task

"""View"""
from ..views.project_board import ProjectBoardView


class ProjectBoardTest(BaseTestCase):
    url = BASE_URL + "boards/"
    task_url = BASE_URL + "tasks/"

    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.team = create_team(self.user, users=[self.user])
        self.board = create_board(self.team)

    # Create board api test
    def test_create_api_valid(self):
        request = {"name": "Sprint 2", "description": "Second sprint", "team_id": str(self.team.id),
                   "creation_time": "2026-10-20T10:00:00Z"}
        data = self.assert_response(self.post(self.url, request), 201)
        board = Board.objects.get(id=data["id"])
        self.assertEqual((board.status, board.created_at.isoformat()), (STATUS_OPEN, "2026-10-20T10:00:00+00:00"))

    def test_create_api_duplicate_name(self):
        self.assert_response(self.post(self.url, {"name": "Sprint 1", "team_id": self.team.id}), 400,
                             "Board" + MESSAGES["already_exists"])

        """ same board name is allowed for other team """
        other_team = create_team(self.user, name="Frontend")
        self.assert_response(self.post(self.url, {"name": "Sprint 1", "team_id": other_team.id}), 201)

    def test_create_api_max_length(self):
        self.assert_response(self.post(self.url, {"name": "n" * 65, "team_id": self.team.id}), 400)
        self.assert_response(self.post(self.url, {"name": "Sprint 2", "description": "d" * 129, "team_id": self.team.id}), 400)

    def test_create_api_invalid_data(self):
        self.assert_response(self.post(self.url, {"name": "Sprint 2", "team_id": "999"}), 404)
        self.assert_response(self.post(self.url, {"name": "Sprint 2"}), 404)
        self.assert_response(self.post(self.url, {"team_id": self.team.id}), 400)
        self.assert_response(self.post(self.url, {"name": "Sprint 2", "team_id": self.team.id, "creation_time": "today"}), 400)

    # List boards api test
    def test_list_api_valid(self):
        create_board(self.team, name="Old sprint", status=STATUS_CLOSED)
        data = self.assert_response(self.get(f"{BASE_URL}teams/{self.team.id}/boards/"), 200)
        self.assertEqual(data, [{"id": str(self.board.id), "name": "Sprint 1"}])

    def test_list_api_not_found(self):
        self.assert_response(self.get(f"{BASE_URL}teams/999/boards/"), 404)

    # Add task api test
    def test_add_task_api_valid(self):
        request = {"title": "Build API", "description": "Write the endpoints", "user_id": str(self.user.id),
                   "board_id": str(self.board.id), "creation_time": "2026-10-21T10:00:00Z"}
        data = self.assert_response(self.post(self.task_url, request), 201)
        task = Task.objects.get(id=data["id"])
        self.assertEqual((task.status, task.board_id, task.user_id), (STATUS_OPEN, self.board.id, self.user.id))

    def test_add_task_api_duplicate_title(self):
        create_task(self.board, self.user)
        request = {"title": "Build API", "user_id": self.user.id, "board_id": self.board.id}
        self.assert_response(self.post(self.task_url, request), 400, "Task" + MESSAGES["already_exists"])

    def test_add_task_api_max_length(self):
        self.assert_response(self.post(self.task_url, {"title": "t" * 65, "user_id": self.user.id, "board_id": self.board.id}), 400)
        request = {"title": "Build API", "description": "d" * 129, "user_id": self.user.id, "board_id": self.board.id}
        self.assert_response(self.post(self.task_url, request), 400)

    def test_add_task_api_invalid_data(self):
        self.assert_response(self.post(self.task_url, {"title": "Build API", "user_id": self.user.id, "board_id": "999"}), 404)
        self.assert_response(self.post(self.task_url, {"title": "Build API", "user_id": "999", "board_id": self.board.id}), 400)
        self.assert_response(self.post(self.task_url, {"user_id": self.user.id, "board_id": self.board.id}), 400)

    def test_add_task_api_closed_board(self):
        board = create_board(self.team, name="Old sprint", status=STATUS_CLOSED)
        request = {"title": "Build API", "user_id": self.user.id, "board_id": board.id}
        self.assert_response(self.post(self.task_url, request), 400, MESSAGES["board_not_open"])

    # Update task status api test
    def test_update_task_status_api_valid(self):
        task = create_task(self.board, self.user)
        for status in TASK_STATUSES:
            self.assert_response(self.put(f"{self.task_url}{task.id}/", {"status": status}), 200)
            self.assertEqual(Task.objects.get(id=task.id).status, status)

    def test_update_task_status_api_invalid_status(self):
        task = create_task(self.board, self.user)
        self.assert_response(self.put(f"{self.task_url}{task.id}/", {"status": "DONE"}), 400, MESSAGES["invalid_status"])
        self.assert_response(self.put(f"{self.task_url}{task.id}/", {}), 400)

    def test_update_task_status_api_not_found(self):
        self.assert_response(self.put(f"{self.task_url}999/", {"status": STATUS_OPEN}), 404)

    # Close board api test
    def test_close_api_valid(self):
        create_task(self.board, self.user, status=STATUS_COMPLETE)
        self.assert_response(self.put(f"{self.url}{self.board.id}/close/"), 200)
        board = Board.objects.get(id=self.board.id)
        self.assertEqual(board.status, STATUS_CLOSED)
        self.assertIsNotNone(board.end_time)

    def test_close_api_without_tasks(self):
        self.assert_response(self.put(f"{self.url}{self.board.id}/close/"), 200)

    def test_close_api_tasks_not_complete(self):
        create_task(self.board, self.user, status=STATUS_COMPLETE)
        create_task(self.board, self.user, title="Write tests", status=STATUS_IN_PROGRESS)
        self.assert_response(self.put(f"{self.url}{self.board.id}/close/"), 400, MESSAGES["tasks_not_complete"])
        self.assertEqual(Board.objects.get(id=self.board.id).status, STATUS_OPEN)

    def test_close_api_already_closed(self):
        board = create_board(self.team, name="Old sprint", status=STATUS_CLOSED)
        self.assert_response(self.put(f"{self.url}{board.id}/close/"), 400, MESSAGES["board_closed"])

    def test_close_api_not_found(self):
        self.assert_response(self.put(f"{self.url}999/close/"), 404)

    # Export board api test
    def test_export_api_valid(self):
        create_task(self.board, self.user, status=STATUS_COMPLETE)
        create_task(self.board, self.user, title="Write tests")

        with tempfile.TemporaryDirectory() as out_dir, override_settings(OUT_DIR=out_dir):
            data = self.assert_response(self.get(f"{self.url}{self.board.id}/export/"), 200)
            with open(os.path.join(out_dir, data["out_file"])) as file:
                content = file.read()

        self.assertEqual(data["out_file"], f"board_{self.board.id}.txt")
        for text in ["Sprint 1", "Backend", "Build API", "Write tests", "1/2 tasks complete"]:
            self.assertIn(text, content)

    def test_export_api_not_found(self):
        self.assert_response(self.get(f"{self.url}999/export/"), 404)

    # Base class api test, json string in and json string out
    def test_base_class_apis(self):
        view = ProjectBoardView()
        board_id = json.loads(view.create_board(json.dumps({"name": "Sprint 2", "team_id": self.team.id})))["id"]
        task = json.loads(view.add_task(json.dumps({"title": "API", "user_id": self.user.id, "board_id": board_id})))
        self.assertEqual(view.update_task_status(json.dumps({"id": task["id"], "status": STATUS_COMPLETE})), "{}")
        self.assertEqual(len(json.loads(view.list_boards(json.dumps({"id": self.team.id})))), 2)
        self.assertEqual(view.close_board(json.dumps({"id": board_id})), "{}")

        with tempfile.TemporaryDirectory() as out_dir, override_settings(OUT_DIR=out_dir):
            self.assertEqual(json.loads(view.export_board(json.dumps({"id": board_id}))), {"out_file": f"board_{board_id}.txt"})

    def test_base_class_invalid_inputs(self):
        view = ProjectBoardView()
        with self.assertRaises(ValidationError):
            view.create_board("not json")
        with self.assertRaises(NotFound):
            view.close_board(json.dumps({"id": "999"}))
        with self.assertRaises(NotFound):
            view.update_task_status(json.dumps({"id": "999", "status": STATUS_OPEN}))
