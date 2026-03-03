from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from crm.models import Team, TeamUser, Task, Comment, Meeting, MeetingUser, Evaluation


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create(
        username="kirill", email="kirill@gmail.com", password="qweRTY123"
    )
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_create_team(user):
    team = Team.objects.create(name="Backend", creator=user)
    assert Team.objects.count() == 1
    assert Team.objects.get(pk=team.pk).name == "Backend"
    assert Team.objects.get(pk=team.pk).creator == user


@pytest.mark.django_db
def test_create_team_user(team, user):
    team_user = TeamUser.objects.create(user=user, team=team, role=TeamUser.Role.ADMIN)
    assert team_user.role == TeamUser.Role.ADMIN


@pytest.mark.django_db
def test_create_task(team, user):
    task = Task.objects.create(
        author=user, team=team, name="Some task", description="description"
    )
    assert task.author == user
    assert task.team == team
    assert task.name == "Some task"


@pytest.mark.django_db
def test_create_task(task, user):
    comment = Comment.objects.create(user=user, task=task, text="comment")
    assert comment.text == "comment"


@pytest.mark.django_db
def test_create_meeting(user):
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(hours=1)
    meeting = Meeting.objects.create(
        creator=user,
        name="meeting",
        description="meeting description",
        start_datetime=start,
        end_datetime=end,
    )
    assert meeting.creator == user
    assert meeting.name == "meeting"


@pytest.mark.django_db
def test_create_meeting_user(user, meeting):
    meeting_user = MeetingUser.objects.create(user=user, meeting=meeting)
    assert meeting_user.user == user
    assert meeting_user.meeting == meeting


@pytest.mark.django_db
def test_create_evaluation(task):
    evaluation = Evaluation.objects.create(
        task=task, evaluation=Evaluation.EvaluationChoices.A
    )
    assert evaluation.task == task
    assert evaluation.evaluation == Evaluation.EvaluationChoices.A
