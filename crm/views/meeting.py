from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from rest_framework.exceptions import PermissionDenied

from crm.forms import MeetingCreateForm
from crm.models import MeetingUser, Meeting


class MeetingCreateView(View):
    """
    View для создания встречи
    """

    def get(self, request):
        """
        Получаем пустую форму для создания встречи
        :param request:
        :return:
        """
        form = MeetingCreateForm()
        return render(request, "crm/meeting_create.html", {"form": form})

    def post(self, request):
        """
        Валидируем полученную форму
        Если валидна - добавляем пользователя как создателя, и сохраняем
        Если нет - возвращаем на страницу с формой
        :param request:
        :return:
        """
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.save()
            MeetingUser.objects.create(user=request.user, meeting=meeting)
            return redirect("meeting_retrieve", meeting_pk=meeting.pk)
        return render(request, "crm/meeting_create.html", {"form": form})


class MeetingAddUserView(View):
    """
    View для добавления пользователя к встрече
    """

    def post(self, request, meeting_pk):
        """
        Обрабатываем запрос на добавления пользователя в встречу
        Валидируем права добавления
        Используем get_or_create для того чтобы добавить пользователя в встречу
        :param request:
        :param meeting_pk:
        :return:
        """
        meeting = get_object_or_404(Meeting, pk=meeting_pk)

        if request.user != meeting.creator:
            raise PermissionDenied("Только владелец может добавлять участников")

        user_pk = request.POST.get("user_pk")
        user = get_object_or_404(User, pk=user_pk)

        MeetingUser.objects.get_or_create(meeting=meeting, user=user)

        messages.success(request, f"Пользователь {user.username} добавлен во встречу")
        return redirect("meeting_retrieve", meeting_pk=meeting.pk)


class MeetingRetrieveView(View):
    """
    View одной встречи
    """

    def get(self, request, meeting_pk):
        """
        Получаем одну встречу и передаем обьект в шаблон
        Также подгружаем связанные сущности
        :param request:
        :param meeting_pk:
        :return:
        """
        meeting = get_object_or_404(
            Meeting.objects.prefetch_related("participants__user"), pk=meeting_pk
        )

        existing_user_ids = meeting.participants.values_list("user_id", flat=True)

        available_users = User.objects.exclude(id__in=existing_user_ids)

        return render(
            request,
            "crm/meeting_retrieve.html",
            {"meeting": meeting, "available_users": available_users},
        )


class MeetingCancelView(View):
    """
    View для отмены встречи
    """

    def post(self, request, meeting_pk):
        """
        Обрабатываем запрос отмены встречи
        :param request:
        :param meeting_pk:
        :return:
        """
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        if request.user != meeting.creator:
            raise PermissionDenied("Только может отменить встречу")
        meeting.delete()
        return redirect("user_profile", user_pk=meeting.creator.pk)


class MeetingListView(View):
    """
    View Списка встреч
    """

    def get(self, request):
        """Просто возвращаем список всех встреч"""
        return render(
            request,
            "crm/meeting_list.html",
            context={"meetings": request.user.meeting_participations.all()},
        )
