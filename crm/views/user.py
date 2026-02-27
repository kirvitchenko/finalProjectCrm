from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import request
from django.views import View

from crm.forms import LoginForm, RegisterForm, UserChangeForm


class RegisterView(View):

    def get(self, request):
        clean_user_register_form = RegisterForm()
        return render(request, 'register.html', context={'form': clean_user_register_form})

    def post(self, request):
        user_register_form = RegisterForm(request.POST)
        if user_register_form.is_valid():
            user = user_register_form.save()
            login(request, user)
            return redirect('profile', user_pk=user.pk)
        else:
            return render(request, 'register.html', context={'form': user_register_form})


class LoginView(View):

    def get(self, request):
        clean_user_login_form = LoginForm()
        return render(request, 'login.html', context={'form': clean_user_login_form})

    def post(self, request):
        user_login_form = LoginForm(request.POST)
        if user_login_form.is_valid():
            login(request, user_login_form.user)
            return render(request, 'profile.html', context={'user': user_login_form.user})
        else:
            clean_user_login_form = LoginForm()
            return render(request, 'login.html', context={'form': clean_user_login_form})


class LogoutView(View):

    def post(self, request):
        logout(request)
        return redirect('home')


class ProfileView(View):

    def get(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
        return render(request, 'profile.html', context={'user': user})


class ProfileUpdateView(View):

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_profile_form = UserChangeForm(instance=user)
        return render(request, 'update_profile.html', context={'form': user_profile_form})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_profile_form = UserChangeForm(request.POST, instance=user)
        if user_profile_form.is_valid():
            user_profile_form.save()
            return redirect('profile', user_pk=user.pk)
        else:
            return render(request, 'update_profile.html', context={'form': user_profile_form})


class UserDelete(View):

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return redirect('home')


