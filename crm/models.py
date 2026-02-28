from datetime import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Team(models.Model):
    """
    Модель команды в системе.

    Команды создаются администратором, он же назначается создателем команды, может добавлять в нее людей.

    name: Название команды
    creator: Пользователь, создавший команду
    created_at: Дата и время создании команды
    updated_at: Дата и время обновления команды
    """
    name = models.CharField(max_length=30)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"


class TeamUser(models.Model):
    """
    Промежуточная таблица для добавления пользователя в команду

    team: внешний ключ на команду
    user: внешний ключ на пользователя добавленного в команду
    role: роль пользователя в команде, определяет его права доступа(user, manager, admin)
    """
    class Role(models.TextChoices):
        USER = "user", "Обычный пользователь"
        MANAGER = "manager", "Менеджер"
        ADMIN = "admin", "Администратор"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(choices=Role, default=Role.USER, max_length=20)

    class Meta:
        """
        Проверка на уникальность. Один пользователь может состоять только в одной команде единовременно.
        """
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_one_team'
            )
        ]


class Task(models.Model):
    """
    Модель задачи в системе.

    Задачи создаются в рамках команды и назначаются на конкретного исполнителя

    author: Пользователь создавший задачачу(admin, manager)
    performer: Исполнитель задачи, назначается из числа администраторов или менеджеров
    team: Внешний ключ на команду к которой относится задача
    status: Статус в котором находится задача, по умолчанию 'open'
    description: Описание задачи
    deadline: Срок, до которого задача должна быть выполнена
    created_at: Дата и время создании задачи
    updated_at: Дата и время обновления задачи
    """

    class Status(models.TextChoices):
        open = "open", "Открыто"
        processing = "processing", "В процессе"
        done = "done", "Выполнено"

    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_tasks"
    )
    performer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="assigned_tasks"
    )
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="tasks")
    status = models.CharField(choices=Status, default=Status.open, max_length=20)
    description = models.TextField()
    deadline = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Comment(models.Model):
    """
    Модель комментария - чат внутри задачи

    created_at: Дата и время создания
    text: Текст комментария
    user: Внешний ключ на пользователя оставившего комментарий
    task: Внешний ключ на задачу к которой относится комментарий
    """
    created_at = models.DateTimeField(default=timezone.now)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Meeting(models.Model):
    """
    Модель встречи в системе.

    Встречи могут назначаться разными пользователями.
    start_datetime, end_datetime - Дата и время начала и конца встречи
    """
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def clean(self):
        """
        Проверям данные на валидность
        1. Дата начала не может быть позже даты конца
        2. Дата начала не может быть в прошлом при создании.
        """
        errors = {}
        if self.start_datetime >= self.end_datetime:
            errors["end_date"] = "Дата окончания должна быть позже даты начала"
        if self.start_datetime < timezone.now():
            errors["start_date"] = "Дата начала не может быть в прошлом"
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Встреча"
        verbose_name_plural = "Встречи"


class MeetingUser(models.Model):
    """
    Запись конкретного пользователя на конкретную встречу.
    user: Внешний ключ на пользователя
    meeting: Внишний ключ на встречу
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meetings")
    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name="participants"
    )

    def clean(self):
        """
        Проверяем правило, согласно которому пользователь не может быть одновременно записан на более чем одну встречу
        """
        overlapping = Meeting.objects.filter(
            participants__user=self.user,
            start_datetime__lt=self.meeting.end_datetime,
            end_datetime__gt=self.meeting.start_datetime,
        ).exclude(pk=self.meeting.pk)

        if overlapping.exists():
            raise ValidationError(...)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Evaluation(models.Model):
    """
    Модель оценки в системе.

    Каждому пользователю выставляется оценка за выполнение каждой задачи

    evaluation: Оценка
    user: Внешний ключ на пользователя
    task: Внешний ключ на задачу
    """
    class EvaluationChoices(models.IntegerChoices):
        A = 5, "Отлично"
        B = 4, "Хорошо"
        C = 3, "Удовлетворительно"
        D = 2, "Неудовлетворительно"
        E = 1, "Плохо"

    evaluation = models.IntegerField(choices=EvaluationChoices, null=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='evaluation')


    @property
    def user(self):
        return self.task.performer

    class Meta:
        """
        Проверяем уникальность - одному пользователю не может быть выставлено более одной оценки за задачу
        """
        constraints = [
            models.UniqueConstraint(
                fields=["task"], name="unique_task_evaluation"
            )
        ]
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
