from django.urls import path

from crm.views.calendar import CalendarView
from crm.views.home import Home
from crm.views.meeting import (
    MeetingListView,
    MeetingCreateView,
    MeetingRetrieveView,
    MeetingAddUserView,
    MeetingCancelView,
)
from crm.views.tasks import (
    TaskListView,
    TaskCreateView,
    TaskRetrieveView,
    TaskUpdateView,
    TaskDeleteView,
    TaskEvaluationView,
    CommentCreateView,
    TaskDoneView,
)
from crm.views.team import (
    TeamCreateView,
    TeamRetrieveView,
    TeamAddUser,
    TeamDeleteUser,
    TeamUpdateUserRole,
    TeamListView,
)
from crm.views.user import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserUpdateView,
    UserDeleteView,
)


urlpatterns = [
    path("home/", Home.as_view(), name="home"),
    # Ссылки для работы с пользователями
    path("register/", UserRegisterView.as_view(), name="user_register"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("logout/", UserLogoutView.as_view(), name="user_logout"),
    path("user/<int:user_pk>/profile/", UserProfileView.as_view(), name="user_profile"),
    path("user/<int:user_pk>/update/", UserUpdateView.as_view(), name="user_update"),
    path("user/<int:user_pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    # Ссылки для работы с командами
    path("teams/create", TeamCreateView.as_view(), name="team_create"),
    path("teams/<int:team_pk>/user/add", TeamAddUser.as_view(), name="team_add_user"),
    path("teams/<int:team_pk>", TeamRetrieveView.as_view(), name="team_retrieve"),
    path(
        "teams/<int:team_pk>/user/<int:user_pk>/delete",
        TeamDeleteUser.as_view(),
        name="team_delete_user",
    ),
    path(
        "teams/<int:team_pk>/user/<int:user_pk>/update",
        TeamUpdateUserRole.as_view(),
        name="team_update_user",
    ),
    path("teams/<int:team_pk>/tasks/", TaskListView.as_view(), name="task_list"),
    path("teams/", TeamListView.as_view(), name="team_list"),
    # Ссылки для работы с задачами
    path("tasks/create/<int:team_pk>/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:task_pk>", TaskRetrieveView.as_view(), name="task_retrieve"),
    path("tasks/<int:task_pk>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:task_pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path(
        "tasks/<int:task_pk>/evaluate>",
        TaskEvaluationView.as_view(),
        name="task_evaluate",
    ),
    path(
        "tasks/<int:task_pk>/comment/",
        CommentCreateView.as_view(),
        name="comment_create",
    ),
    path("tasks/<int:task_pk>/task_done", TaskDoneView.as_view(), name="task_done"),
    # Ссылки для работы со встречами
    path("meetings/", MeetingListView.as_view(), name="meeting_list"),
    path("meetings/create/", MeetingCreateView.as_view(), name="meeting_create"),
    path(
        "meetings/<int:meeting_pk>/",
        MeetingRetrieveView.as_view(),
        name="meeting_retrieve",
    ),
    path(
        "meetings/<int:meeting_pk>/add-user/",
        MeetingAddUserView.as_view(),
        name="meeting_add_user",
    ),
    path(
        "meetings/<int:meeting_pk>/cancel/",
        MeetingCancelView.as_view(),
        name="meeting_cancel",
    ),
    path("calendar/", CalendarView.as_view(), name="calendar"),  # 1
    path(
        "calendar/<int:year>/<int:month>/",
        CalendarView.as_view(),
        name="calendar_month",
    ),  # 2
    path(
        "calendar/<int:year>/<int:month>/<int:day>/",
        CalendarView.as_view(),
        name="calendar_day",
    ),
]  # 3
