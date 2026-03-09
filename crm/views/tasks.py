from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from crm.forms import TaskCreateForm, TaskUpdateForm, EvaluationForm, CommentCreateForm
from crm.models import Task, Evaluation, Team, TeamUser
from crm.permissions import ManagerRequiredMixin, AdminRequiredMixin, TaskOwnerMixin, TaskPerformerMixin, \
    MemberRequiredMixin, TaskTeamInjectorMixin


class TaskCreateView(LoginRequiredMixin, ManagerRequiredMixin, View):
    """
    View для создания задачи в команде
    """

    def get(self, request, team_pk):
        """
        Получаем форму для создания задачи
        :param request:
        :param team_pk:
        :return:
        """
        form = TaskCreateForm()
        return render(request, "crm/task_create.html", {"form": form})

    def post(self, request, team_pk):
        """
        Обрабатываем форму для создания задачи
        Добавляем к обьекту атрибуты author, team
        :param request:
        :param team_pk:
        :return:
        """
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    task = form.save(commit=False)
                    team = get_object_or_404(Team, pk=team_pk)
                    task.author = request.user
                    task.team = team
                    task.save()
                return redirect("task_retrieve", task_pk=task.pk)
            except IntegrityError as e:
                messages.error(request, f"Ошибка в форме: {e}")
        return render(request, "crm/task_create.html", {"form": form})


class TaskListView(LoginRequiredMixin, View):
    """
    View для получения списка задач

    """

    def get(self, request, team_pk):
        """
        Получаем список задач для конкретной команды
        Также реализована пагинация по 10 элементов на странице
        :param request:
        :param team_pk:
        :return:
        """
        tasks = (
            Task.objects.filter(team__pk=team_pk)
            .prefetch_related("evaluation")
            .order_by("-created_at")
        )

        team_user = TeamUser.objects.filter(team_id=team_pk, user=request.user).first()
        user_role = team_user.role if team_user else None

        paginator = Paginator(tasks, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "crm/task_list.html",
            {
                "page_obj": page_obj,
                "team_pk": team_pk,
                "user_role": user_role,
            },
        )


class TaskRetrieveView(LoginRequiredMixin, View):
    """
    View для получения задачи
    """

    def get(self, request, task_pk):
        task = get_object_or_404(
            Task.objects.select_related("author", "team").prefetch_related(
                "comments", "comments__user"
            ),
            pk=task_pk,
        )

        evaluation = getattr(task, "evaluation", None)

        context = {"task": task, "evaluation": evaluation}
        if request.user.is_superuser:
            context["evaluation_form"] = EvaluationForm(instance=evaluation)
        return render(request, "crm/task_retrieve.html", context)


class TaskUpdateView(LoginRequiredMixin, TaskOwnerMixin, View):
    """
    View для изменения задачи
    """

    def get(self, request, task_pk):
        """
        Получаем форму и обьект задачи для обновления
        :param request:
        :param task_pk:
        :return:
        """
        form = TaskUpdateForm(instance=self.task)
        return render(request, "crm/task_update.html", {"form": form, "task": self.task})

    def post(self, request, task_pk):
        """
        Обрабатываем форму обновленной задачи,
        Если прошло валидацию - сохраняем
        Если назначен исполнитель - меняем статус задачи на processing
        :param request:
        :param task_pk:
        :return:
        """
        form = TaskUpdateForm(request.POST, instance=self.task)
        if form.is_valid():
            try:
                with transaction.atomic():
                    task = form.save(commit=False)
                    if task.performer:
                        task.status = Task.Status.processing
                    task.save()
                    return redirect("task_retrieve", task_pk=task.pk)
            except IntegrityError as e:
                messages.error(request, f"Ошибка в форме: {e}")
        return render(request, "crm/task_update.html", {"form": form, "task": self.task})


class TaskDoneView(LoginRequiredMixin, TaskPerformerMixin, View):
    """
    View для того что бы отметить задачу как выполненную
    """

    def post(self, request, task_pk):
        if self.task.status == Task.Status.done:
            messages.warning(request, "Задача уже выполнена")
            return redirect("task_retrieve", task_pk=self.task.pk)
        try:
            self.task.status = Task.Status.done
            self.task.save()
            messages.success(request, "Задача отмечена как выполненная")
        except IntegrityError as e:
            messages.error(request, f"Ошибка: {e}")
        return redirect("task_retrieve", task_pk=self.task.pk)


class TaskDeleteView(LoginRequiredMixin, TaskOwnerMixin, View):
    """
    View для того чтобы удалить задачу
    """

    def post(self, request, task_pk):
        try:
            self.task.delete()
        except IntegrityError as e:
            messages.error(request, f"Ошибка: {e}")
        return redirect("team_retrieve", team_pk=self.task.team.pk)


class TaskEvaluationView(LoginRequiredMixin, TaskTeamInjectorMixin, AdminRequiredMixin, View):
    """
    View для оценки задачи
    """

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        evaluation, created = Evaluation.objects.update_or_create(
            task=task, defaults={"evaluation": request.POST.get("evaluation")}
        )
        messages.success(
            request,
            f"Оценка {evaluation.get_evaluation_display()} сохранена для задачи",
        )
        return redirect("task_retrieve", task_pk=task.pk)


class CommentCreateView(LoginRequiredMixin, TaskTeamInjectorMixin, MemberRequiredMixin, View):
    """
    View для комментирования задачи
    """

    def post(self, request, task_pk):
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.task = self.task
                    comment.save()
            except IntegrityError as e:
                messages.error(request, f"Ошибка: {e}")
        return redirect("task_retrieve", task_pk=task_pk)
