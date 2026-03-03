from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from crm.models import TeamUser


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
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            self.user = request.user
            self.user_role = None
            self.team = None
            return super().dispatch(request, *args, **kwargs)

        team_pk = kwargs.get("team_pk")

        if not team_pk:
            raise PermissionDenied("Не указана команда")

        team_user = TeamUser.objects.filter(team_id=team_pk, user=request.user).first()

        if not team_user:
            messages.error(request, "Вы не состоите в этой команде")
            return redirect("team_list")

        self.user = request.user
        self.user_role = team_user.role
        self.team = team_user.team

        if not self.has_required_role():
            messages.error(request, f"Нужны права: {self.get_required_roles()}")
            return redirect("team_retrieve", team_pk=team_pk)

        return super().dispatch(request, *args, **kwargs)

    def has_required_role(self):
        return True

    def get_required_role(self):
        return True


class AdminRequiredMixin(TeamRoleMixin):
    """
    Класс для проверки на роль адмнистратора
    """

    def has_required_role(self):
        return self.user_role == TeamUser.Role.ADMIN or self.user.is_superuser

    def get_required_role(self):
        return [TeamUser.Role.ADMIN]


class ManagerRequiredMixin(TeamRoleMixin):
    """
    Класс для проверки на роль менеджера
    """

    def has_required_role(self):
        return (
            self.user_role in [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER]
            or self.user.is_superuser
        )

    def get_required_role(self):
        return [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER]


class MemberRequiredMixin(TeamRoleMixin):
    """
    Класс для проверки на членство в команде
    """

    def has_required_role(self):
        return self.user_role in [
            TeamUser.Role.ADMIN,
            TeamUser.Role.MANAGER,
            TeamUser.Role.USER,
        ]

    def get_required_role(self):
        return [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER, TeamUser.Role.USER]


def check_task_owner(user, task):
    """Проверяем является ли пользователь создателем задачи"""
    if not task.author == user:
        raise PermissionDenied("Только создатель может управлять задачей")


class StaffRequiredMixin(UserPassesTestMixin):
    """Проверка на роль администартора всего приложения(Django-admin)"""

    def test_func(self):
        return self.request.user.is_staff
