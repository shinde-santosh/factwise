import json
from django.test import TestCase

from factwise_app.models import User, Team, Board, Task
from utility.constants import STATUS_OPEN

HEADERS = {"content_type": "application/json"}


def create_user(name="santosh", display_name="Santosh Shinde"):
    return User.objects.create(name=name, display_name=display_name)


def create_team(admin, name="Backend", users=()):
    team = Team.objects.create(name=name, description="Backend team", admin=admin)
    team.users.add(*users)
    return team


def create_board(team, name="Sprint 1", status=STATUS_OPEN):
    return Board.objects.create(name=name, description="First sprint", team=team, status=status)


def create_task(board, user, title="Build API", status=STATUS_OPEN):
    return Task.objects.create(title=title, description="Write the endpoints", board=board, user=user, status=status)


class BaseTestCase(TestCase):

    def get(self, url):
        return self.client.get(url, **HEADERS)

    def post(self, url, data=None):
        return self.client.post(url, data=json.dumps(data or {}), **HEADERS)

    def put(self, url, data=None):
        return self.client.put(url, data=json.dumps(data or {}), **HEADERS)

    def assert_response(self, response, code, message=None):
        self.assertEqual(response.status_code, code, response.content)
        self.assertEqual(response.json()["code"], code)
        self.assertEqual(response.json()["success"], code < 400)
        if message:
            self.assertIn(message, response.json()["message"])
        return response.json()["data"]
