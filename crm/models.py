from datetime import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=30)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

class TeamUser(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'Обычный пользователь'
        MANAGER = 'manager', 'Менеджер'
        ADMIN = 'admin', 'Администратор'

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(choices=Role, default=Role.USER, max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'team'],
                name='unique_user_team'
            )
        ]


class Task(models.Model):
    class Status(models.TextChoices):
        open = 'open', 'Открыто'
        processing = 'processing', 'В процессе'
        done = 'done', 'Выполнено'

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    performer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='tasks')
    status = models.CharField(choices=Status, default=Status.open, max_length=20)
    description = models.TextField()
    deadline = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

class Comment(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Meeting(models.Model):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def clean(self):
        errors = {}
        if self.start_datetime >= self.end_datetime:
            errors['end_date'] = 'Дата окончания должна быть позже даты начала'
        if self.start_datetime < timezone.now():
            errors['start_date'] = 'Дата начала не может быть в прошлом'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Встреча'
        verbose_name_plural = 'Встречи'

class MeetingUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meetings')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')

    def clean(self):
        overlapping = Meeting.objects.filter(
            participants__user=self.user,
            start_datetime__lt=self.meeting.end_datetime,
            end_datetime__gt=self.meeting.start_datetime
        ).exclude(pk=self.meeting.pk)

        if overlapping.exists():
            raise ValidationError(...)
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Evaluation(models.Model):
    class EvaluationChoices(models.IntegerChoices):
        A = 5, "Отлично"
        B = 4, "Хорошо"
        C = 3, "Удовлетворительно"
        D = 2, "Неудовлитворительно"
        E = 1, "Плохо"

    evaluation = models.IntegerField(choices=EvaluationChoices, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'task'],
                name='unique_task_evaluation_for_user'
            )
        ]
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"