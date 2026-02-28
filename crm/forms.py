from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from crm.models import Team, TeamUser, Task, Evaluation


class RegisterForm(forms.ModelForm):
    repeated_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "password"]
        widgets = {"password": forms.PasswordInput}

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeated_password")

        if password != repeated_password:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean_username(self):
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
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        try:
            user = User.objects.get(email=email)
            self.user = authenticate(username=user.username, password=password)
        except User.DoesNotExists:
            self.user = None
        if not self.user:
            raise forms.ValidationError("Неверный логин или пароль")
        return cleaned_data


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

class UpdateUserTeamRoleForm(forms.ModelForm):
    class Meta:
        model = TeamUser
        fields = ['role']

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['team', 'status', 'description', 'deadline']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

class TaskUpdateForm(forms.ModelForm):
    class Meta:
        fields = ['performer', 'deadline', 'description', 'status']

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['evaluation']
        widgets = {
            'evaluation': forms.Select
        }