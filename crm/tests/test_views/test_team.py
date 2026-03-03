import pytest
from pytest_django.asserts import assertContains

from crm.models import Team, TeamUser


@pytest.fixture
def test_create_team(client):
    response = client.post("teams/create", {"name": "django-team"})
    assert response.status_code == 302
    assert Team.objects.count() == 1


@pytest.mark.django_db
def test_task_list(client, team):
    response = client.get("/teams/")
    assertContains(response, team.name)


@pytest.mark.django_db
def test_task_retrieve(client, team):
    response = client.get(f"/teams/{team.pk}")
    assert response.status_code == 200
    assertContains(response, team.name)


@pytest.mark.django_db
def test_team_task_add_user(superuser, client, team, user):
    client.force_login(superuser)
    response = client.post(f"/teams/{team.pk}/user/add", {"user_pk": user.pk})
    assert response.status_code == 302
    assert TeamUser.objects.count() == 1
