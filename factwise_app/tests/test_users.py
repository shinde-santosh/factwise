import json
from rest_framework.exceptions import NotFound, ValidationError

from utility.constants import *
from utility.test_utility import *

"""Model"""
from ..models import User

"""View"""
from ..views.users import UsersView


class UsersTest(BaseTestCase):
    url = BASE_URL + "users/"

    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.team = create_team(self.user, users=[self.user])

    # Create api test
    def test_create_api_valid(self):
        data = self.assert_response(self.post(self.url, {"name": "rahul", "display_name": "Rahul Patil"}), 201)
        self.assertTrue(User.objects.filter(id=data["id"], name="rahul").exists())

    def test_create_api_duplicate_name(self):
        self.assert_response(self.post(self.url, {"name": "santosh", "display_name": "Other"}), 400)

    def test_create_api_name_max_length(self):
        self.assert_response(self.post(self.url, {"name": "n" * 65, "display_name": "Rahul"}), 400)

    def test_create_api_display_name_max_length(self):
        self.assert_response(self.post(self.url, {"name": "rahul", "display_name": "d" * 64}), 201)
        self.assert_response(self.post(self.url, {"name": "amit", "display_name": "d" * 65}), 400,
                             MESSAGES["display_name_max"])

    def test_create_api_required_fields(self):
        self.assert_response(self.post(self.url, {"name": "rahul"}), 400)
        self.assert_response(self.post(self.url, {"display_name": "Rahul"}), 400)

    def test_create_api_invalid_json(self):
        response = self.client.post(self.url, data="{bad json", **HEADERS)
        self.assertEqual(response.status_code, 400)

    # List api test
    def test_list_api_valid(self):
        data = self.assert_response(self.get(self.url), 200)
        self.assertEqual(data, [{
            "name": "santosh",
            "display_name": "Santosh Shinde",
            "creation_time": self.user.created_at.isoformat(),
        }])

    # Describe api test
    def test_describe_api_valid(self):
        data = self.assert_response(self.get(f"{self.url}{self.user.id}/"), 200)
        self.assertEqual(set(data.keys()), {"name", "display_name", "creation_time"})

    def test_describe_api_not_found(self):
        self.assert_response(self.get(f"{self.url}999/"), 404, "User" + MESSAGES["not_found"])

    # Update api test
    def test_update_api_valid(self):
        self.assert_response(self.put(f"{self.url}{self.user.id}/", {"display_name": "d" * 128}), 200)
        self.assertEqual(User.objects.get(id=self.user.id).display_name, "d" * 128)

    def test_update_api_display_name_max_length(self):
        self.assert_response(self.put(f"{self.url}{self.user.id}/", {"display_name": "d" * 129}), 400)

    def test_update_api_name_cannot_update(self):
        self.assert_response(self.put(f"{self.url}{self.user.id}/", {"name": "other"}), 400,
                             MESSAGES["name_cannot_update"])
        self.assert_response(self.put(f"{self.url}{self.user.id}/", {"name": "santosh", "display_name": "S"}), 200)

    def test_update_api_not_found(self):
        self.assert_response(self.put(f"{self.url}999/", {"display_name": "S"}), 404)

    # User teams api test
    def test_user_teams_api_valid(self):
        data = self.assert_response(self.get(f"{self.url}{self.user.id}/teams/"), 200)
        self.assertEqual(data, [{
            "name": "Backend",
            "description": "Backend team",
            "creation_time": self.team.created_at.isoformat(),
        }])

    def test_user_teams_api_not_found(self):
        self.assert_response(self.get(f"{self.url}999/teams/"), 404)

    # Base class api test, json string in and json string out
    def test_base_class_apis(self):
        view = UsersView()
        self.assertEqual(json.loads(view.create_user(json.dumps({"name": "rahul", "display_name": "Rahul"}))).keys(), {"id"})
        self.assertIsInstance(json.loads(view.list_users()), list)
        self.assertEqual(json.loads(view.describe_user(json.dumps({"id": str(self.user.id)})))["name"], "santosh")
        self.assertEqual(view.update_user(json.dumps({"id": self.user.id, "user": {"display_name": "S"}})), "{}")
        self.assertEqual(len(json.loads(view.get_user_teams(json.dumps({"id": self.user.id})))), 1)

    def test_base_class_invalid_inputs(self):
        view = UsersView()
        with self.assertRaises(ValidationError):
            view.create_user("not json")
        with self.assertRaises(ValidationError):
            view.create_user(json.dumps(["name"]))
        with self.assertRaises(NotFound):
            view.describe_user(json.dumps({"id": "999"}))
