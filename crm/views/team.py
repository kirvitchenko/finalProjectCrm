from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View

from crm.forms import TeamForm, UpdateUserTeamRoleForm
from crm.models import Team, TeamUser
from crm.permissions import AdminRequiredMixin, StaffRequiredMixin


class TeamCreateView(StaffRequiredMixin, View):
    """
    View для создания команды
    """

    def get(self, request):
        """
        Получаем пустую форму создания команды
        :param request:
        :return:
        """
        form = TeamForm()
        return render(request, "crm/team_create.html", {"form": form})

    def post(self, request):
        """
        Обрабатываем форму
        Если валидно - добавляем текущего пользователя как создателя и сохраняем
        :param request:
        :return:
        """
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.creator = request.user
            team.save()
            return redirect("team_retrieve", team_pk=team.pk)
        return render(request, "crm/team_create.html", {"form": form})


class TeamListView(View):
    """
    View для списка команд
    """

    def get(self, request):
        teams = Team.objects.all()
        return render(request, "crm/team_list.html", {"teams": teams})


class TeamRetrieveView(View):
    """
    View для одной команды
    """

    def get(self, request, team_pk):
        """
        Помимо обьекта команды возвращаем доступных пользователей для приглашения
        :param request:
        :param team_pk:
        :return:
        """
        team = get_object_or_404(Team.objects.prefetch_related("members"), pk=team_pk)
        available_users = User.objects.exclude(memberships__isnull=False)
        return render(
            request,
            "crm/team_retrieve.html",
            {"team": team, "available_users": available_users},
        )


class BaseTeamView(View):
    """Базовый класс для всех views, работающих с командами"""

    def get_team(self, team_pk):
        return get_object_or_404(Team, pk=team_pk)

    def get_user(self, user_pk):
        return get_object_or_404(User, pk=user_pk)

    def get_team_user(self, team_pk, user_pk):
        return get_object_or_404(TeamUser, team_id=team_pk, user_id=user_pk)


class TeamAddUser(AdminRequiredMixin, BaseTeamView):
    """
    View для добавления пользователя в команду
    """

    def post(self, request, team_pk):
        user_pk = request.POST.get("user_pk")
        team = self.get_team(team_pk)
        user = self.get_user(user_pk)
        if TeamUser.objects.filter(user=user).exists():
            messages.error(
                request, f"Пользователь {user.username} уже состоит в команде"
            )
            return redirect("team_retrieve", team_pk=team_pk)

        TeamUser.objects.create(user=user, team=team, role=TeamUser.Role.USER)
        messages.success(request, f"Пользователь {user.username} добавлен в команду")
        return redirect("team_retrieve", team_pk=team_pk)


class TeamDeleteUser(AdminRequiredMixin, BaseTeamView):
    """
    View для удаления пользователя из команды
    """

    def post(self, request, team_pk, user_pk):
        team_user = self.get_team_user(team_pk, user_pk)

        if team_user.team.creator == team_user.user:
            messages.error(request, "Нельзя удалить создателя команды")
            return redirect("team_retrieve", team_pk=team_pk)

        team_user.delete()
        messages.success(request, "Пользователь удален из команды")
        return redirect("team_retrieve", team_pk=team_pk)


class TeamUpdateUserRole(AdminRequiredMixin, BaseTeamView):
    """
    Обновляем роль пользователя в команде
    """

    def get(self, request, team_pk, user_pk):
        """
        Получаем страницу обновления пользователя
        :param request:
        :param team_pk:
        :param user_pk:
        :return:
        """
        team_user = self.get_team_user(team_pk, user_pk)
        form = UpdateUserTeamRoleForm(instance=team_user)
        return render(
            request, "crm/team_role_update.html", {"form": form, "team_user": team_user}
        )

    def post(self, request, team_pk, user_pk):
        """
        Обновляем роль пользователя
        :param request:
        :param team_pk:
        :param user_pk:
        :return:
        """
        team_user = self.get_team_user(team_pk, user_pk)
        form = UpdateUserTeamRoleForm(request.POST, instance=team_user)
        if form.is_valid():
            form.save()
            return redirect("team_retrieve", team_pk=team_pk)
        return render(
            request, "crm/team_role_update.html", {"form": form, "team_user": team_user}
        )
