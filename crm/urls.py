from django.urls import path

from crm.views.home import Home
from crm.views.team import TeamCreateView, TeamRetrieveView, TeamAddUser, TeamDeleteUser, TeamUpdateUserRole
from crm.views.user import UserRegisterView, UserLoginView, UserLogoutView, UserProfileView, UserUpdateView, \
    UserDeleteView




urlpatterns = [
    path('home/', Home.as_view(), name='home'),

    #Ссылки для работы с пользователями
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('user/<int:user_pk>/profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/<int:user_pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('user/<int:user_pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    #Ссылки для работы с командами
    path('team/create', TeamCreateView.as_view(), name='team_create'),
    path('team/<int:team_pk>', TeamRetrieveView.as_view(), name='team_retrieve'),
    path('team/<int:team_pk>/user/<int:user_pk>/add', TeamAddUser.as_view(), name='team_add_user'),
    path('team/<int:team_pk>/user/<int:user_pk>/delete', TeamDeleteUser.as_view(), name='team_delete_user'),
    path('team/<int:team_pk>/user/<int:user_pk>/update', TeamUpdateUserRole.as_view(), name='team_update_user'),
]