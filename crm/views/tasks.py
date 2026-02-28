from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from crm.forms import TaskCreateForm, TaskUpdateForm, EvaluationForm
from crm.models import Task, Evaluation


class TaskCreateView(View):

    def get(self, request):
        form = TaskCreateForm()
        return render(request, 'task_create.html', {'form': form})

    def post(self, request):
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            return redirect('task_profile', task_pk=task.pk)
        messages.error(request, 'Ошибка в форме')
        return render(request, 'task_create.html', {'form': form})


class TaskListView(View):

    def get(self, request, team_pk):
        tasks = Task.objects.filter(team__pk=team_pk).prefetch_related('evaluations')
        return render(request, 'task_list.html', {'tasks': tasks})


class TaskRetrieveView(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task.objects
                                 .select_related('author', 'team')
                                 .prefetch_related('comments', 'comments__user'), pk=task_pk)

        evaluation = getattr(task, 'evaluation', None)

        context = {
            'task': task,
            'evaluation': evaluation
        }
        if request.user.is_superuser:
            context['evaluation_form'] = EvaluationForm(instance=evaluation)
        return render(request, 'task_retrieve.html', context)


class TaskUpdateView(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        form = TaskUpdateForm(instance=task)
        return render(request, 'task_update.html', {'form': form})

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        form = TaskUpdateForm(request.POST, instance=task)  # ✅ form
        if form.is_valid():
            form.save()
            return redirect('task_profile', task_pk=task.pk)
        return render(request, 'task_update.html', {'form': form})


class TaskDeleteView(View):

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task.delete()
        return redirect('team_retrieve', team_pk=task.team.pk)


class TaskEvaluationView(View):

    def post(self, request, task_pk):
        if not request.user.is_superuser:
            messages.error(request, 'Только администратор может оценивать задачи')
            return redirect('task_retrieve', task_pk=task_pk)
        task = get_object_or_404(Task, pk=task_pk)
        evaluation, created = Evaluation.update_or_create(
            task=task,
            defaults={
                'evaluation': request.POST.get('evaluation')
            }
        )
        messages.success(
            request,
            f'Оценка {evaluation.get_evaluation_display()} сохранена для задачи'
        )
        return redirect('task_retrieve', task_pk=task.pk)