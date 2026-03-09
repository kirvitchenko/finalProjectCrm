from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import ModelForm

from crm.models import Team, TeamUser, Task, Evaluation, Meeting, MeetingUser, Comment


class RegisterForm(forms.ModelForm):
    """
    Форма регистрация пользователя
    """

    repeated_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "password"]
        widgets = {"password": forms.PasswordInput}

    def clean(self):
        """
        Проверяем что введенные пароль равны
        :return:
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeated_password")

        if password != repeated_password:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def clean_email(self):
        """
        Проверяем на уникальность email при создании
        :return:
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_username(self):
        """
        Проверяем на уникальность username при создании
        :return:
        """
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Форма для аутентификация пользователя
    """

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """
        Проверяем что пользователь существует и ввел правильные данные
        Если пользователь не существует или ввел неправльные данные выбрасываем исключение
        :return:
        """
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        try:
            user = User.objects.get(email=email)
            self.user = authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            self.user = None
        if not self.user:
            raise forms.ValidationError("Неверный логин или пароль")
        return cleaned_data


class UserChangeForm(forms.ModelForm):
    """
    Форма для редактирования профиля и данных пользователя
    """

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name"]


class TeamForm(forms.ModelForm):
    """
    Форма для создания команды
    """

    class Meta:
        model = Team
        fields = ["name"]


class UpdateUserTeamRoleForm(forms.ModelForm):
    """
    Форма для изменения роли пользователя в команде
    """

    class Meta:
        model = TeamUser
        fields = ["role"]


class TaskCreateForm(forms.ModelForm):
    """
    Форма для создания задачи
    """

    class Meta:
        model = Task
        fields = ["name", "status", "description", "deadline"]
        widgets = {"deadline": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class TaskForm(forms.ModelForm):
    """
    Форма для просмотра одной задачи
    """

    class Meta:
        model = Task
        fields = "__all__"


class TaskUpdateForm(forms.ModelForm):
    """
    Форма для изменения данных задачи
    """

    class Meta:
        model = Task
        fields = ["performer", "deadline", "description", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['performer'].queryset = User.objects.filter(
                memberships__team=self.instance.team
                )


class EvaluationForm(forms.ModelForm):
    """
    Форма для проставленния оценки за задачу
    """

    class Meta:
        model = Evaluation
        fields = ["evaluation"]
        widgets = {"evaluation": forms.RadioSelect}


class CommentCreateForm(ModelForm):
    """
    Форма для добавления комментария к задаче
    """

    class Meta:
        model = Comment
        fields = ["text"]


class MeetingCreateForm(forms.ModelForm):
    """
    Форма для создания встречи
    """

    class Meta:
        model = Meeting
        fields = ["start_datetime", "end_datetime", "name", "description"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class MeetingAddUserForm(forms.ModelForm):
    """
    Форма для добавления пользователя в встречу
    """

    class Meta:
        model = MeetingUser
        fields = ["user"]
