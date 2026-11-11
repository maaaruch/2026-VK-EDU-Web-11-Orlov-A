# ДЗ 2

Сайт вопросов и ответов на Django.

## Запуск

В папке проекта:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd web-edu
python manage.py runserver
```

Сайт откроется по адресу http://localhost:8000/.

Можно запустить через Docker из папки проекта:

```bash
docker compose up --build
```

Остановить — `docker compose down`.

## Страницы

- `/` — новые вопросы
- `/hot/` — популярные вопросы
- `/tag/css/` — вопросы по тегу
- `/question/1/` — вопрос и ответы
- `/ask/` — задать вопрос
- `/login/` — вход
- `/signup/` — регистрация
- `/profile/` — профиль

