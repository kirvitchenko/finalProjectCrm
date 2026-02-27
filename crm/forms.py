from django import forms
from crm.models import Team


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ['name']