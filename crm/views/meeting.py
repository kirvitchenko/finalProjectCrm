from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from rest_framework.exceptions import PermissionDenied

from crm.forms import MeetingCreateForm
from crm.models import MeetingUser, Meeting


class MeetingCreateView(View):
    def get(self, request):
        form = MeetingCreateForm()
        return render(request, "crm/meeting_create.html", {"form": form})

    def post(self, request):
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.save()
            MeetingUser.objects.create(user=request.user, meeting=meeting)
            return redirect('meeting_retrieve', meeting_pk=meeting.pk)
        return render(request, "crm/meeting_create.html", {"form": form})


class MeetingAddUserView(View):
    def post(self, request, meeting_pk):
        meeting = get_object_or_404(Meeting, pk=meeting_pk)  # ← исправлено!

        if request.user != meeting.creator:
            raise PermissionDenied("Только владелец может добавлять участников")

        user_pk = request.POST.get('user_pk')
        user = get_object_or_404(User, pk=user_pk)

        MeetingUser.objects.get_or_create(
            meeting=meeting,
            user=user
        )

        messages.success(request, f"Пользователь {user.username} добавлен во встречу")
        return redirect("meeting_retrieve", meeting_pk=meeting.pk)



class MeetingRetrieveView(View):
    def get(self, request, meeting_pk):
        meeting = get_object_or_404(
            Meeting.objects.prefetch_related('participants__user'),
            pk=meeting_pk
        )

        existing_user_ids = meeting.participants.values_list('user_id', flat=True)

        available_users = User.objects.exclude(id__in=existing_user_ids)

        return render(request, 'crm/meeting_retrieve.html', {
            'meeting': meeting,
            'available_users': available_users
        })

class MeetingCancelView(View):
    def post(self, request, meeting_pk):
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        if request.user != meeting.creator:
            raise PermissionDenied("Только может отменить встречу")
        meeting.delete()
        return redirect("user_profile", user_pk=meeting.creator.pk)


class MeetingListView(View):
    def get(self, request):
        return render(
            request,
            "crm/meeting_list.html",
            context={"meetings": request.user.meeting_participations.all()},
        )
