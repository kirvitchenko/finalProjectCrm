from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from crm.forms import TaskCreateForm, TaskUpdateForm
from crm.models import Task


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
        return render(request, 'task_create.html', context={'form': form})


class TaskProfile(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task.objects.prefetch_related('comments', 'comments__user'), pk=task_pk)
        return render(request, 'task_profile.html', context={'task': task})

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
        return render(request, 'task_update.html', context={'form': form})

class TaskDeleteView(View):

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task.delete()
        return redirect('team_profile', team_pk=task.team.pk)