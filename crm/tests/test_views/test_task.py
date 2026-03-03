import pytest

from crm.models import Task


@pytest.mark.django_db
def test_create_task(superuser, client, team):
    client.force_login(superuser)
    response = client.post(
        f"/tasks/create/{team.pk}/",
        {
            "name": "test task",
            "status": Task.Status.open,
            "description": "task for test",
        },
    )
    assert response.status_code == 302
    assert Task.objects.count() == 1

