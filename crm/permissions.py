from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404

from crm.models import TeamUser, Task, Meeting


class TeamRoleMixin:
    """
    Общий класс для проверки роли пользователя

    1. Сначала проверяем аутентифицирован ли пользователь и есть ли у него права суперпользователя
    2. Проверяем укзаана ли команда
    3. Проверяем состоит ли пользователь в этой команде
    4. Присваиваем атрибуты класса
    5. Проверяем конкретную роль через классы наследники
    """

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        team_pk = kwargs.get("team_pk")

        if not team_pk:
            raise PermissionDenied("Не указана команда")

        try:
            team_user = TeamUser.objects.get(
                team_id=team_pk,
                user=request.user
            )
        except TeamUser.DoesNotExist:
            messages.error(request, "Вы не состоите в этой команде")
            return redirect("team_list")


        self.user = request.user
        self.user_role = team_user.role
        self.team = team_user.team

        if not self.has_required_role():
            messages.error(request, f"Нужны права: {self.get_required_role()}")
            return redirect("team_retrieve", team_pk=team_pk)

        return super().dispatch(request, *args, **kwargs)

    def has_required_role(self):
        return self.user_role in self.required_roles

    def get_required_role(self):
        return self.required_roles


class AdminRequiredMixin(TeamRoleMixin):
    """
        Класс для проверки на роль адмнистратора
        """

    required_roles = [TeamUser.Role.ADMIN]


class ManagerRequiredMixin(TeamRoleMixin):
    """
        Класс для проверки на роль менеджера
        """
    required_roles = [
        TeamUser.Role.ADMIN,
        TeamUser.Role.MANAGER,
    ]


class MemberRequiredMixin(TeamRoleMixin):
    """
       Класс для проверки на членство в команде
       """
    required_roles = [
        TeamUser.Role.ADMIN,
        TeamUser.Role.MANAGER,
        TeamUser.Role.USER,
    ]


class StaffRequiredMixin(UserPassesTestMixin):
    """Проверка на роль администартора всего приложения(Django-admin)"""

    def test_func(self):
        return self.request.user.is_staff

class TaskOwnerMixin:
    """
        Проверяет, что текущий пользователь является автором задачи
        """
    def dispatch(self, request, *args, **kwargs):

        task_pk = kwargs.get('task_pk') or kwargs.get('pk')
        self.task = get_object_or_404(Task, pk=task_pk)
        if request.user != self.task.author:
            raise PermissionDenied('Только автор может редактировать задачу')
        return super().dispatch(request, *args, **kwargs)


class TaskPerformerMixin:
    """
        Проверяет, что текущий пользователь является автором задачи
        """
    def dispatch(self, request, *args, **kwargs):

        task_pk = kwargs.get('task_pk') or kwargs.get('pk')
        self.task = get_object_or_404(Task, pk=task_pk)
        if request.user != self.task.performer:
            raise PermissionDenied('Только исполнитель может может менять статус задачи')
        return super().dispatch(request, *args, **kwargs)

class MeetingCreatorMixin:
    """
    Проверяет является ли пользователь создателем встречи
    """
    def dispatch(self, request, *args, **kwargs):

        meeting_pk = kwargs.get('meeting_pk') or kwargs.get('pk')
        self.meeting = get_object_or_404(Meeting, pk=meeting_pk)
        if request.user != self.meeting.creator:
            raise PermissionDenied('Только создатель может редактировать встречу')
        return super().dispatch(request, *args, **kwargs)

class UserDataOwnerMixin:
    """
    Проверяет является ли пользователь хозяином аккаунта
    """
    def dispatch(self, request, *args, **kwargs):

        user_pk = kwargs.get('user_pk') or kwargs.get('pk')
        self.user = get_object_or_404(User, pk=user_pk)
        if request.user != self.user:
            raise PermissionDenied("Только владелец может управлять аккаунтом")
        return super().dispatch(request, *args, **kwargs)

class TaskTeamInjectorMixin:
    """
    Добавляет team_pk в kwargs на основе task_pk
    """
    def dispatch(self, request, *args, **kwargs):
        task_pk = kwargs.get('task_pk')
        if task_pk:
            self.task = get_object_or_404(Task, pk=task_pk)
            kwargs['team_pk'] = self.task.team.pk
        return super().dispatch(request, *args, **kwargs)