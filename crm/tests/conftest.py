from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from crm.models import Team, Task, Meeting


@pytest.fixture
def user():
    return User.objects.create_user(email='email@email.com',username="username", password="password")


@pytest.fixture
def team(user):
    return Team.objects.create(name="team", creator=user)


@pytest.fixture
def task(user, team):
    return Task.objects.create(
        author=user, team=team, name="task", description="task_description"
    )


@pytest.fixture
def meeting(user):
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(hours=1)
    meeting = Meeting.objects.create(
        creator=user,
        name="meeting",
        description="description",
        start_datetime=start,
        end_datetime=end,
    )
    return meeting
