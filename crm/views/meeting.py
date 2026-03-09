from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from crm.forms import MeetingCreateForm
from crm.models import MeetingUser, Meeting
from crm.permissions import MeetingCreatorMixin


class MeetingCreateView(LoginRequiredMixin, View):
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
            try:
                with transaction.atomic():
                    meeting = form.save(commit=False)
                    meeting.creator = request.user
                    meeting.save()
                    MeetingUser.objects.create(user=request.user, meeting=meeting)
                return redirect("meeting_retrieve", meeting_pk=meeting.pk)
            except IntegrityError as e:
                messages.error(request, f'Ошибка при сохранении: {e}')
        return render(request, "crm/meeting_create.html", {"form": form})


class MeetingAddUserView(LoginRequiredMixin, MeetingCreatorMixin, View):
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
        user_pk = request.POST.get("user_pk")
        user = get_object_or_404(User, pk=user_pk)

        _, created = MeetingUser.objects.get_or_create(meeting=self.meeting, user=user)

        if created:
            messages.success(request, f"Пользователь {user.username} добавлен")
        else:
            messages.warning(request, f"Пользователь {user.username} уже во встрече")
        return redirect("meeting_retrieve", meeting_pk=self.meeting.pk)


class MeetingRetrieveView(LoginRequiredMixin, View):
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


class MeetingCancelView(LoginRequiredMixin, MeetingCreatorMixin, View):
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
        try:
            self.meeting.delete()
            messages.success(request, "Встреча отменена")
        except IntegrityError as e:
            messages.error(request, f'Ошибка при сохранении: {e}')

        return redirect("user_profile", user_pk=self.meeting.creator.pk)


class MeetingListView(LoginRequiredMixin, View):
    """
    View Списка встреч
    """

    def get(self, request):
        """Просто возвращаем список всех встреч"""
        meetings = Meeting.objects.filter(participants__user=request.user)
        return render(
            request,
            "crm/meeting_list.html",
            context={"meetings": meetings},
        )
