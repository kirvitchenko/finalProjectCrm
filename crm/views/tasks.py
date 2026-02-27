from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from crm.forms import TaskCreateForm, TaskUpdateForm
from crm.models import Task


class TaskCreateView(View):

    def get(self, request):
        clean_create_task_form = TaskCreateForm()
        return render(request, 'task_create.html', context={'form': clean_create_task_form})

    def post(self, request):
        create_task_form = TaskCreateForm(request.POST)
        if create_task_form.is_valid():
            created_task = create_task_form.save(commit=False)
            created_task.author = request.user
            created_task.save()
            return redirect('task_profile', task_pk=created_task.pk)
        messages.error(request, f'Ошибка в форме')
        return render(request, 'task_create.html', context={'form': create_task_form})

class TaskProfile(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        return render(request, 'task_profile.html', context={'task': task})

class TaskUpdateView(View):

    def get(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task_update_form = TaskUpdateForm(instance=task)
        return render(request, 'task_update.html', context={'form': task_update_form})


    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task_update_form = TaskUpdateForm(request.POST, instance=task)
        if task_update_form.is_valid():
            task_update_form.save()
            return redirect('task_profile', task_pk=task.pk)
        return render(request, 'task_update.html', context={'form': task_update_form})

class TaskDeleteView(View):

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task.delete()
        return redirect('team_profile', team_pk=task.team.pk)