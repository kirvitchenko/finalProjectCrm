from django.views import View
from django.views.generic import ListView
from rest_framework.renderers import TemplateHTMLRenderer

from crm.forms import TeamForm
from crm.models import Team


class TeamView(View):
    model = Team
    template_name = None
    context_object_name = 'teams'
    paginate_by = 10

    def post(self, request):
        team_form = TeamForm(request.POST)
        if team_form.is_valid():
            team_form.save()
            return None
        null_form = TeamForm()
        return None

class TeamListView(ListView):
    model = Team
    template_name = None
    context_object_name = 'teams'
    paginate_by = 10

    def get_queryset(self):
        return Team.objects.filter(id=self.request.team_id)
