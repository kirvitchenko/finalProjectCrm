from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from crm.forms import LoginForm, RegisterForm, UserChangeForm
from crm.models import Evaluation


class UserRegisterView(View):
    """
    View для регистрации пользователя
    """

    def get(self, request):
        """
        Получаем форму для регистрации
        :param request:
        :return:
        """
        form = RegisterForm()
        return render(request, "crm/user_register.html", {"form": form})

    def post(self, request):
        """
        Обрабатывем форму для регистрации
        :param request:
        :return:
        """
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("user_profile", user_pk=user.pk)
        else:
            return render(request, "crm/user_register.html", {"form": form})


class UserLoginView(View):
    """
    View для входа в аккаунт
    """

    def get(self, request):
        """
        Получаем форму для входа
        """
        clean_form = LoginForm()
        return render(request, "crm/user_login.html", {"form": clean_form})

    def post(self, request):
        """
        Проверяем корректность введенных данных
        Создаем сессию
        :param request:
        :return:
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("user_profile", user_pk=form.user.pk)
        else:
            return render(request, "crm/user_login.html", {"form": form})


class UserLogoutView(View, LoginRequiredMixin):
    """
    View для выхода
    """

    def post(self, request):
        logout(request)
        return redirect("home")


class UserProfileView(View, LoginRequiredMixin):
    """
    View для просмотра профиля пользователя
    """

    def get(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
        evaluations = Evaluation.objects.filter(task__performer=user).select_related(
            "task"
        )
        return render(
            request, "crm/user_profile.html", {"user": user, "evaluations": evaluations}
        )


class UserUpdateView(View, LoginRequiredMixin):
    """
    View для обновления данных пользователя
    """

    def get(self, request, user_pk):
        """
        Получаем форму для обновления
        :param request:
        :param user_pk:
        :return:
        """
        user = get_object_or_404(User, pk=user_pk)
        if request.user != user:
            raise PermissionDenied("Только владелец может редактировать аккаунт")
        form = UserChangeForm(instance=user)
        return render(request, "crm/user_update.html", {"form": form})

    def post(self, request, user_pk):
        """
        Проверяем заполенненую форму
        :param request:
        :param user_pk:
        :return:
        """
        user = get_object_or_404(User, pk=user_pk)
        if request.user != user:
            raise PermissionDenied("Только владелец может редактировать аккаунт")
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_profile", user_pk=user.pk)
        else:
            return render(request, "crm/user_update.html", {"form": form})


class UserDeleteView(View, LoginRequiredMixin):
    """
    View для удаления пользователя
    """

    def post(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
        if request.user != user:
            raise PermissionDenied("Только владелец может удалять аккаунт")
        user.delete()
        return redirect("home")
