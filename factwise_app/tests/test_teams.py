import json
from rest_framework.exceptions import NotFound, ValidationError

from utility.constants import *
from utility.test_utility import *

"""Model"""
from ..models import Team, User

"""View"""
from ..views.teams import TeamsView


class TeamsTest(BaseTestCase):
    url = BASE_URL + "teams/"

    @classmethod
    def setUpTestData(self):
        self.user = create_user()
        self.member = create_user(name="rahul", display_name="Rahul Patil")
        self.team = create_team(self.user, users=[self.user])

    # Create api test
    def test_create_api_valid(self):
        data = self.assert_response(self.post(self.url, {"name": "Frontend", "description": "UI", "admin": str(self.user.id)}), 201)
        self.assertTrue(Team.objects.filter(id=data["id"], name="Frontend", admin=self.user).exists())

    def test_create_api_duplicate_name(self):
        self.assert_response(self.post(self.url, {"name": "Backend", "admin": self.user.id}), 400)

    def test_create_api_max_length(self):
        self.assert_response(self.post(self.url, {"name": "n" * 65, "admin": self.user.id}), 400)
        self.assert_response(self.post(self.url, {"name": "Frontend", "description": "d" * 129, "admin": self.user.id}), 400)

    def test_create_api_invalid_admin(self):
        self.assert_response(self.post(self.url, {"name": "Frontend", "admin": "999"}), 400)
        self.assert_response(self.post(self.url, {"name": "Frontend"}), 400)

    # List api test
    def test_list_api_valid(self):
        data = self.assert_response(self.get(self.url), 200)
        self.assertEqual(data, [{
            "name": "Backend",
            "description": "Backend team",
            "creation_time": self.team.created_at.isoformat(),
            "admin": str(self.user.id),
        }])

    # Describe api test
    def test_describe_api_valid(self):
        data = self.assert_response(self.get(f"{self.url}{self.team.id}/"), 200)
        self.assertEqual(set(data.keys()), {"name", "description", "creation_time", "admin"})

    def test_describe_api_not_found(self):
        self.assert_response(self.get(f"{self.url}999/"), 404, "Team" + MESSAGES["not_found"])

    # Update api test
    def test_update_api_valid(self):
        data = {"name": "Platform", "description": "Platform team", "admin": str(self.member.id)}
        self.assert_response(self.put(f"{self.url}{self.team.id}/", data), 200)
        team = Team.objects.get(id=self.team.id)
        self.assertEqual((team.name, team.description, team.admin_id), ("Platform", "Platform team", self.member.id))

    def test_update_api_duplicate_name(self):
        create_team(self.user, name="Frontend")
        self.assert_response(self.put(f"{self.url}{self.team.id}/", {"name": "Frontend"}), 400)

    def test_update_api_max_length(self):
        self.assert_response(self.put(f"{self.url}{self.team.id}/", {"name": "n" * 65}), 400)
        self.assert_response(self.put(f"{self.url}{self.team.id}/", {"description": "d" * 129}), 400)

    def test_update_api_not_found(self):
        self.assert_response(self.put(f"{self.url}999/", {"name": "Platform"}), 404)

    # Add users api test
    def test_add_users_api_valid(self):
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": [str(self.member.id)]}), 200)
        self.assertTrue(self.team.users.filter(id=self.member.id).exists())

    def test_add_users_api_invalid_users(self):
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": ["999"]}), 404)
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": []}), 400)
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": "1"}), 400)
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": ["abc"]}), 400)

    def test_add_users_api_max_users(self):
        users = User.objects.bulk_create([User(name=f"user{i}", display_name="User") for i in range(MAX_TEAM_USERS)])
        user_ids = [user.id for user in users]

        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": user_ids[1:]}), 200)
        self.assertEqual(self.team.users.count(), MAX_TEAM_USERS)
        self.assert_response(self.post(f"{self.url}{self.team.id}/add-users/", {"users": user_ids[:1]}), 400,
                             MESSAGES["max_team_users"])

    def test_add_users_api_not_found(self):
        self.assert_response(self.post(f"{self.url}999/add-users/", {"users": [self.member.id]}), 404)

    # Remove users api test
    def test_remove_users_api_valid(self):
        self.team.users.add(self.member)
        self.assert_response(self.post(f"{self.url}{self.team.id}/remove-users/", {"users": [self.member.id]}), 200)
        self.assertFalse(self.team.users.filter(id=self.member.id).exists())

    def test_remove_users_api_invalid_users(self):
        self.assert_response(self.post(f"{self.url}{self.team.id}/remove-users/", {"users": ["999"]}), 404)
        self.assert_response(self.post(f"{self.url}{self.team.id}/remove-users/", {"users": []}), 400)

    # List team users api test
    def test_team_users_api_valid(self):
        data = self.assert_response(self.get(f"{self.url}{self.team.id}/users/"), 200)
        self.assertEqual(data, [{"id": str(self.user.id), "name": "santosh", "display_name": "Santosh Shinde"}])

    def test_team_users_api_not_found(self):
        self.assert_response(self.get(f"{self.url}999/users/"), 404)

    # Base class api test, json string in and json string out
    def test_base_class_apis(self):
        view = TeamsView()
        self.assertEqual(json.loads(view.create_team(json.dumps({"name": "Frontend", "admin": self.user.id}))).keys(), {"id"})
        self.assertIsInstance(json.loads(view.list_teams()), list)
        self.assertEqual(json.loads(view.describe_team(json.dumps({"id": self.team.id})))["name"], "Backend")
        self.assertEqual(view.update_team(json.dumps({"id": self.team.id, "team": {"description": "x"}})), "{}")
        self.assertEqual(view.add_users_to_team(json.dumps({"id": self.team.id, "users": [self.member.id]})), "{}")
        self.assertEqual(len(json.loads(view.list_team_users(json.dumps({"id": self.team.id})))), 2)
        self.assertEqual(view.remove_users_from_team(json.dumps({"id": self.team.id, "users": [self.member.id]})), "{}")

    def test_base_class_invalid_inputs(self):
        view = TeamsView()
        with self.assertRaises(ValidationError):
            view.create_team("not json")
        with self.assertRaises(ValidationError):
            view.update_team(json.dumps({"id": self.team.id, "team": "Backend"}))
        with self.assertRaises(NotFound):
            view.describe_team(json.dumps({"id": "999"}))
