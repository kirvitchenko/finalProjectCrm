# CRM System

Простая система управления задачами и встречами для команд.

## Функционал

- 👥 **Пользователи**: регистрация, вход, просмотр и редактирование профиля
- 👑 **Команды**: создание, управление участниками, роли (admin/manager/user)
- 📋 **Задачи**: создание, назначение исполнителя, статусы, комментарии
- 📊 **Оценки**: администратор оценивает выполненные задачи (1-5)
- 📅 **Встречи**: планирование, добавление участников, проверка пересечений
- 🗓️ **Календарь**: просмотр задач и встреч по дням и месяцам

## Установка и запуск

```bash
git clone <url-репозитория>
cd finalProjectCrm
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# CRM System

Веб-приложение для управления командами, задачами, встречами и календарём.

---

## 📁 Структура проекта

crm/
├── models.py              # Модели данных
├── forms.py               # Формы
├── permissions.py         # Миксины для прав доступа
├── urls.py                # Маршруты
├── views/                 # Представления
│   ├── user.py            # Пользователи
│   ├── team.py            # Команды
│   ├── tasks.py           # Задачи
│   ├── meeting.py         # Встречи
│   └── calendar.py        # Календарь
├── templates/
│   └── crm/               # HTML шаблоны
└── tests/                 # Тесты
---

## 🌐 Основные маршруты

| URL | Описание |
|------|----------|
| `/register/` | Регистрация |
| `/login/` | Вход |
| `/logout/` | Выход |
| `/user/<int:user_pk>/profile/` | Профиль пользователя |
| `/user/<int:user_pk>/update/` | Редактирование профиля |
| `/user/<int:user_pk>/delete/` | Удаление аккаунта |
| `/teams/` | Список команд |
| `/teams/<int:team_pk>/` | Страница команды |
| `/teams/<int:team_pk>/user/add` | Добавление участника |
| `/teams/<int:team_pk>/user/<int:user_pk>/delete` | Удаление участника |
| `/teams/<int:team_pk>/user/<int:user_pk>/update` | Изменение роли |
| `/tasks/<int:task_pk>/` | Детали задачи |
| `/tasks/create/<int:team_pk>/` | Создание задачи |
| `/tasks/<int:task_pk>/update/` | Редактирование задачи |
| `/tasks/<int:task_pk>/delete/` | Удаление задачи |
| `/tasks/<int:task_pk>/done/` | Отметить выполненной |
| `/tasks/<int:task_pk>/evaluate/` | Оценить задачу |
| `/tasks/<int:task_pk>/comment/` | Добавить комментарий |
| `/meetings/` | Список встреч |
| `/meetings/create/` | Создание встречи |
| `/meetings/<int:meeting_pk>/` | Детали встречи |
| `/meetings/<int:meeting_pk>/add-user/` | Добавить участника |
| `/meetings/<int:meeting_pk>/cancel/` | Отменить встречу |
| `/calendar/` | Календарь (текущий месяц) |
| `/calendar/<int:year>/<int:month>/` | Календарь за указанный месяц |
| `/calendar/<int:year>/<int:month>/<int:day>/` | Дневной вид |

---

## 🗄 Модели данных

### User (встроенная модель Django)

- `username`
- `email`
- `password`
- `first_name`
- `last_name`
- `is_active`
- `is_staff`
- `is_superuser`

---

### Team

- `name` — название команды  
- `creator` — создатель (ForeignKey на User)  
- `created_at` — дата создания  
- `updated_at` — дата обновления  

---

### TeamUser

- `team` — команда (ForeignKey)  
- `user` — пользователь (ForeignKey)  
- `role` — роль (`user`, `manager`, `admin`)  

---

### Task

- `name` — название задачи  
- `description` — описание  
- `author` — автор (ForeignKey)  
- `performer` — исполнитель (ForeignKey)  
- `team` — команда (ForeignKey)  
- `status` — статус (`open`, `processing`, `done`)  
- `deadline` — срок выполнения  
- `created_at`
- `updated_at`

---

### Comment

- `text` — текст комментария  
- `user` — автор (ForeignKey)  
- `task` — задача (ForeignKey)  
- `created_at`

---

### Meeting

- `name` — название встречи  
- `description` — описание  
- `creator` — создатель (ForeignKey)  
- `start_datetime` — начало  
- `end_datetime` — окончание  

---

### MeetingUser

- `user` — участник (ForeignKey)  
- `meeting` — встреча (ForeignKey)  

---

### Evaluation

- `evaluation` — оценка (1–5)  
- `task` — задача (ForeignKey)  
- `user` — оцениваемый пользователь (ForeignKey)  

---

## 🔐 Права доступа

| Действие | Admin | Manager | User |
|-----------|--------|----------|------|
| Создание команды | ✅ | ❌ | ❌ |
| Управление участниками | ✅ | ❌ | ❌ |
| Создание задачи | ✅ | ✅ | ❌ |
| Редактирование задачи | ✅ | ✅ | ❌ |
| Удаление задачи | ✅ | ✅ | ❌ |
| Выполнение задачи | ✅ | ✅ | ✅ |
| Оценка задачи | ✅ | ❌ | ❌ |
| Создание встречи | ✅ | ✅ | ✅ |
| Отмена встречи | ✅ (свои) | ✅ (свои) | ✅ (свои) |

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=crm --cov-report=term-missing

# Создание HTML-отчета о покрытии
pytest --cov=crm --cov-report=html
# Отчет будет в папке htmlcov/
```

---

## Примеры запросов и ответов

### Регистрация

**Запрос:**
```http
POST /register/
Content-Type: application/x-www-form-urlencoded

email=user@example.com&username=john&password=123456&repeated_password=123456
Ответ: Редирект на /user/1/profile/

Вход
Запрос:

http
POST /login/
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=123456
Ответ: Редирект на /user/1/profile/

Создание команды (только admin)
Запрос:

http
POST /teams/create
Content-Type: application/x-www-form-urlencoded

name=Разработчики
Ответ: Редирект на /teams/1/

## 📦 Зависимости

- Django 6.0+
- pytest
- pytest-django
- pytest-cov
- python-dotenv
- ruff

---

## ⚙ Переменные окружения

Создайте файл `.env` в корне проекта:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your_db
```