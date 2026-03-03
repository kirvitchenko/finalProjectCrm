from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from django.views import View
from crm.models import Meeting, Task


class CalendarView(View):
    """Единый календарь для отображения задач и встреч"""

    def get(self, request):
        today = timezone.now()

        # Безопасное получение параметров
        try:
            year = int(request.GET.get('year', today.year))
            month = int(request.GET.get('month', today.month))
            day = int(request.GET.get('day', today.day))
        except (ValueError, TypeError):
            year = today.year
            month = today.month
            day = today.day

        mode = request.GET.get('mode', 'month')

        # Задачи без дедлайна (нужны для обоих режимов)
        tasks_without_deadline = Task.objects.filter(
            performer=request.user,
            deadline__isnull=True
        )

        if mode == 'day':
            date = datetime(year, month, day)
            tasks = Task.objects.filter(
                performer=request.user,
                deadline__date=date
            )
            meetings = Meeting.objects.filter(
                participants__user=request.user,
                start_datetime__date=date
            )
            return render(request, 'crm/calendar_day.html', {
                'date': date,
                'tasks': tasks,
                'meetings': meetings,
                'tasks_without_deadline': tasks_without_deadline,
            })
        else:
            # Месячный вид
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, monthrange(year, month)[1])

            tasks = Task.objects.filter(
                performer=request.user,
                deadline__date__range=[first_day, last_day]
            )
            meetings = Meeting.objects.filter(
                participants__user=request.user,
                start_datetime__date__range=[first_day, last_day]
            )

            # Названия месяцев
            month_names = {
                1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
                5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
            }

            # Предыдущий и следующий месяц
            if month == 1:
                prev_month = 12
                prev_year = year - 1
            else:
                prev_month = month - 1
                prev_year = year

            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year

            # Сетка дней
            month_days = []
            week = [None] * first_day.weekday()

            for d in range(1, last_day.day + 1):
                week.append(d)
                if len(week) == 7:
                    month_days.append(week)
                    week = []

            if week:
                month_days.append(week + [None] * (7 - len(week)))

            return render(request, 'crm/calendar_month.html', {
                'year': year,
                'month': month,
                'month_name': month_names[month],
                'prev_year': prev_year,
                'prev_month': prev_month,
                'prev_month_name': month_names[prev_month],
                'next_year': next_year,
                'next_month': next_month,
                'next_month_name': month_names[next_month],
                'today': today,
                'month_days': month_days,
                'tasks': tasks,
                'tasks_without_deadline': tasks_without_deadline,
                'meetings': meetings,
            })