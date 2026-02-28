from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.views import View

from crm.forms import LoginForm, RegisterForm, UserChangeForm
from crm.models import Evaluation


class UserRegisterView(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, 'user_register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile', user_pk=user.pk)
        else:
            return render(request, 'user_register.html', {'form': form})


class UserLoginView(View):

    def get(self, request):
        clean_form = LoginForm()
        return render(request, 'user_login.html', {'form': clean_form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return render(request, 'user_profile.html', {'user': form.user})
        else:
            return render(request, 'user_login.html', {'form': form})


class UserLogoutView(View):

    def post(self, request):
        logout(request)
        return redirect('home')


class UserProfileView(View):

    def get(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
        evaluations = Evaluation.objects.filter(task__performer=user).select_related('task')
        return render(request, 'user_profile.html', {'user': user, 'evaluations': evaluations})


class UserUpdateView(View):

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserChangeForm(instance=user)
        return render(request, 'profile_update.html', {'form': form})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', user_pk=user.pk)
        else:
            return render(request, 'profile_update.html', {'form': form})


class UserDeleteView(View):

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return redirect('home')


