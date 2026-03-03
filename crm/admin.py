from django.contrib import admin
from django.contrib.auth.models import User

from crm.models import Team, Task, TeamUser, Meeting, MeetingUser, Comment, Evaluation

admin.site.register([Team, Task, TeamUser, Meeting, MeetingUser, Comment, Evaluation])
