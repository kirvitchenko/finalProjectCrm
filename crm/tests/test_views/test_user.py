import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register(client):
    response = client.post(
        "/register/",
        {
            "email": "test@test.com",
            "username": "username",
            "password": "password",
            "repeated_password": "password",
        },
    )
    assert response.status_code == 302
    assert User.objects.count() == 1

    user = User.objects.first()
    assert user.email == "test@test.com"
    assert user.username == "username"


@pytest.mark.django_db
def test_login_success(client, user):
    """Успешный вход должен редиректить на профиль"""
    response = client.post('/login/', {
        'email': 'email@email.com',
        'password': 'password'
    })

    assert response.status_code == 302  # редирект
    assert response.url == f"/user/{user.pk}/profile/"  # куда редирект

    # Проверяем, что пользователь действительно залогинен
    response = client.get(response.url)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated


@pytest.mark.django_db
def test_login_fail(client, user):
    """Неудачный вход должен показать форму с ошибкой"""
    response = client.post('/login/', {
        'email': 'wrong@email.com',
        'password': 'wrong'
    })

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].errors
