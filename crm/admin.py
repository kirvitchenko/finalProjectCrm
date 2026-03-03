from django.contrib import admin

from crm.models import Team, Task, TeamUser, Meeting, MeetingUser, Comment, Evaluation

admin.site.register([Team, Task, TeamUser, Meeting, MeetingUser, Comment, Evaluation])
