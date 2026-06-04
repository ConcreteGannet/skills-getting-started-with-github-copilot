import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_adds_participant(client):
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={duplicate_email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant(client):
    activity_name = "Chess Club"
    participant = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={participant}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {participant} from {activity_name}"}
    assert participant not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    activity_name = "Chess Club"
    missing_email = "absent@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={missing_email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"
