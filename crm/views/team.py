from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView

from crm.forms import TeamForm, UpdateUserTeamRoleForm
from crm.models import Team, TeamUser


class TeamCreateView(View):

    def get(self, request):
        form = TeamForm()
        return render(request, 'team_create.html', {'form': form})

    def post(self, request):
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.creator = request.user
            team.save()
            TeamUser.objects.create(user=request.user, team=team, role=TeamUser.Role.ADMIN)
            return redirect('team_profile', team_pk=team.pk)
        return render(request, 'team_create.html', {'form': form})


class TeamRetrieveView(View):

    def get(self, request, team_pk):
        team = get_object_or_404(Team.objects.prefetch_related('members'), pk=team_pk)
        return render(request, 'team_retrieve.html', {'team': team})


class BaseTeamView(View):
    """Базовый класс для всех views, работающих с командами"""

    def get_team(self, team_pk):
        return get_object_or_404(Team, pk=team_pk)

    def get_user(self, user_pk):
        return get_object_or_404(User, pk=user_pk)

    def get_team_user(self, team_pk, user_pk):
        return get_object_or_404(TeamUser, team_id=team_pk, user_id=user_pk)


class TeamAddUser(BaseTeamView):

    def post(self, request, team_pk, user_pk):
        team = self.get_team(team_pk)
        user = self.get_user(user_pk)
        if TeamUser.objects.filter(user=user).exists():
            messages.error(request, f'Пользователь {user.username} уже состоит в команде')
            return redirect('team_retrieve', team_pk=team_pk)

        TeamUser.objects.create(
            user=user,
            team=team,
            role=TeamUser.Role.USER
        )
        messages.success(request, f'Пользователь {user.username} добавлен в команду')
        return redirect('team_retrieve', team_pk=team_pk)


class TeamDeleteUser(BaseTeamView):

    def post(self, request, team_pk, user_pk):
        team_user = self.get_team_user(team_pk, user_pk)

        if team_user.team.creator == team_user.user:
            messages.error(request, 'Нельзя удалить создателя команды')
            return redirect('team_retrieve', team_pk=team_pk)

        team_user.delete()
        messages.success(request, 'Пользователь удален из команды')
        return redirect('team_retrieve', team_pk=team_pk)


class UpdateUserTeamRole(BaseTeamView):

    def get(self, request, team_pk, user_pk):
        team_user = self.get_team_user(team_pk, user_pk)
        form = UpdateUserTeamRoleForm(instance=team_user)
        return render(request, 'role_update.html', {'form': form, 'team_user': team_user})

    def post(self, request, team_pk, user_pk):
        team_user = self.get_team_user(team_pk, user_pk)
        form = UpdateUserTeamRoleForm(request.POST, instance=team_user)
        if form.is_valid():
            form.save()
            return redirect('team_retrieve', team_pk=team_pk)
        return render(request, 'role_update.html', {'form': form, 'team_user': team_user})
