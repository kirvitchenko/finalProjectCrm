from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from rest_framework.exceptions import PermissionDenied

from crm.forms import MeetingCreateForm
from crm.models import MeetingUser, Meeting


class MeetingCreateView(View):
    def get(self, request):
        form = MeetingCreateForm()
        return render(request, "meeting_create.html", {"form": form})

    def post(self, request):
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.save()
            MeetingUser.objects.create(user=request.user, meeting=meeting)
            return render(request, "meeting_retrieve.html", {"meeting": meeting})
        return render(request, "meeting_create.html", {"form": form})


class MeetingAddUserView(View):
    def get(self, request, meeting_pk):
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        if request.user != meeting.creator:
            raise PermissionDenied('Только владелец может добавлять участников')
        form = MeetingCreateForm()
        return render(request, "meeting_user_create.html", {"form": form})

    def post(self, request, meeting_pk):
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            meeting_user = form.save(commit=False)
            meeting = get_object_or_404(MeetingUser, pk=meeting_pk)
            if request.user != meeting.creator:
                raise PermissionDenied('Только владелец может добавлять участников')
            meeting_user.meeting = meeting
            meeting_user.save()
            return redirect("meeting_retrieve", meeting_pk=meeting_pk)
        return render(request, "meeting_user_create.html", {"form": form})


class MeetingCancelView(View):
    def post(self, request, meeting_pk):
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        if request.user != meeting.creator:
            raise PermissionDenied('Только может отменить встречу')
        meeting.delete()
        return redirect("user_profile", user_pk=meeting.creator.pk)


class MeetingListView(View):
    def get(self, request):
        return render(
            request,
            "meeting_list.html",
            context={"meetings": request.user.meeting_participations.all()},
        )
