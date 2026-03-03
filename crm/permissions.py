from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from crm.models import TeamUser


class TeamRoleMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        print(f"=== TeamRoleMixin.dispatch ===")
        print(f"User: {request.user}")
        print(f"team_pk from kwargs: {kwargs.get('team_pk')}")

        team_pk = kwargs.get("team_pk")
        print(f"Checking membership for team {team_pk}, user {request.user}")
        print(f"Exists: {TeamUser.objects.filter(team_id=team_pk, user=request.user).exists()}")
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
    def has_required_role(self):
        return self.user_role == TeamUser.Role.ADMIN

    def get_required_role(self):
        return [TeamUser.Role.ADMIN]


class ManagerRequiredMixin(TeamRoleMixin):
    def has_required_role(self):
        return self.user_role in [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER] or self.user.is_superuser()

    def get_required_role(self):
        return [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER]


class MemberRequiredMixin(TeamRoleMixin):
    def has_required_role(self):
        return self.user_role in [
            TeamUser.Role.ADMIN,
            TeamUser.Role.MANAGER,
            TeamUser.Role.USER,
        ]

    def get_required_role(self):
        return [TeamUser.Role.ADMIN, TeamUser.Role.MANAGER, TeamUser.Role.USER]


def check_task_owner(user, task):
    if not task.author == user:
        raise PermissionDenied("Только создатель может управлять задачей")


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
