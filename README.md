# AIMART - Интернет-магазин

AIMART - это современный интернет-магазин, построенный на Django. Проект включает в себя функциональность оформления заказов, оплаты через различные платежные системы и управления заказами.

## Основные возможности

- Оформление заказов
- Оплата через банковские карты
- Оплата через Kaspi
- Сохранение карт для быстрой оплаты
- Отслеживание статуса заказа
- Административная панель для управления заказами

## Технологии

- Python 3.8+
- Django 4.2+
- PostgreSQL
- Redis
- Celery
- QR-коды для оплаты
- Bootstrap 5
- jQuery

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/aimart.git
cd aimart
```

2. Создайте виртуальное окружение и активируйте его:

```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл .env и настройте переменные окружения:

```bash
cp .env.example .env
```

5. Примените миграции:

```bash
python manage.py migrate
```

6. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

7. Запустите сервер разработки:

```bash
python manage.py runserver
```

## Структура проекта

```
aimart/
├── orders/              # Приложение для работы с заказами
│   ├── models.py        # Модели данных
│   ├── views.py         # Представления
│   ├── forms.py         # Формы
│   ├── urls.py          # URL-маршруты
│   └── templates/       # Шаблоны
├── products/            # Приложение для работы с товарами
├── accounts/            # Приложение для работы с пользователями
├── static/              # Статические файлы
├── media/               # Медиа-файлы
└── manage.py            # Скрипт управления Django
```

## Использование

1. Зарегистрируйтесь или войдите в систему
2. Добавьте товары в корзину
3. Перейдите к оформлению заказа
4. Выберите способ оплаты
5. Следуйте инструкциям для завершения оплаты

## Разработка

### Запуск тестов

```bash
python manage.py test
```

### Проверка кода

```bash
flake8
black .
isort .
```

### Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

## Лицензия

MIT

## Авторы

- Ваше имя - [GitHub](https://github.com/yourusername)

## Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории проекта.
