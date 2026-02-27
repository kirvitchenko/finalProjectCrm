from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from rest_framework.renderers import TemplateHTMLRenderer

from crm.forms import TeamForm
from crm.models import Team, TeamUser


class TeamView(View):
    model = Team
    template_name = 'team'
    context_object_name = "teams"
    paginate_by = 10

    def post(self, request):
        team_create_form = TeamForm(request.POST)
        if team_create_form.is_valid():
            team = team_create_form.save()
            return redirect('team_list', team_pk=team.pk)
        clean_team_create_form = TeamForm()
        return render(request, 'team_create.html', context={'form': clean_team_create_form})


class TeamListView(View):
    model = Team
    template_name = "team"
    context_object_name = "team"

    def get_queryset(self):
        return Team.objects.filter(id=self.request.team_id).prefetch_related('members')

class TeamAddUser(View):

    def post(self, request, team_pk, user_pk):
        team = get_object_or_404(Team, pk=team_pk)
        user = get_object_or_404(User, pk=user_pk)
        team_user = TeamUser.object.create(user=user, team=team)
        return redirect('team_profile', team_pk=team_pk)

