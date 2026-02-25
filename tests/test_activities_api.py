import copy
import urllib.parse


def test_root_redirects_to_static(client):
    # Arrange: `client` fixture provided by tests/conftest.py

    # Act
    # Don't follow redirects so we can assert the redirect response itself
    resp = client.get("/", allow_redirects=False)

    # Assert
    assert resp.status_code == 307
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities_returns_dict(client):
    # Arrange

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Known activity from initial snapshot
    assert "Chess Club" in data
    activity = data["Chess Club"]
    for key in ("description", "schedule", "max_participants", "participants"):
        assert key in activity


def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure email not present initially
    initial = client.get("/activities").json()
    assert email not in initial[activity]["participants"]

    # Act
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.post(path, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Verify participant was added
    updated = client.get("/activities").json()
    assert email in updated[activity]["participants"]


def test_signup_nonexistent_activity(client):
    # Arrange
    activity = "NoSuchActivity"
    email = "x@x.com"

    # Act
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.post(path, params={"email": email})

    # Assert
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Activity not found"


def test_signup_already_signed_up(client):
    # Arrange: use an email that exists in initial data for Chess Club
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.post(path, params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert resp.json().get("detail") == "Student already signed up"


def test_unregister_success(client):
    # Arrange: add a participant to remove
    activity = "Chess Club"
    email = "tempuser@example.com"
    add_path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    add_resp = client.post(add_path, params={"email": email})
    assert add_resp.status_code == 200

    # Act: remove the participant
    del_path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.delete(del_path, params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # Verify participant removed
    updated = client.get("/activities").json()
    assert email not in updated[activity]["participants"]


def test_unregister_nonexistent_activity(client):
    # Arrange
    activity = "NoSuchActivity"
    email = "x@x.com"

    # Act
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.delete(path, params={"email": email})

    # Assert
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Activity not found"


def test_unregister_participant_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "notpresent@example.com"

    # Ensure email not present
    initial = client.get("/activities").json()
    assert email not in initial[activity]["participants"]

    # Act
    path = f"/activities/{urllib.parse.quote(activity, safe='')}/signup"
    resp = client.delete(path, params={"email": email})

    # Assert
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Participant not found"
