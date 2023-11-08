## Проект «Фудграм»
Фудграм — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
Проект доступен по [адресу](https://yaalex.ddns.net)
### Технологии:
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud, GitHub Actions
### Развертывание проекта:
1. На сервере создайте директорию для приложения:
    ```bash
    mkdir foodgram
    ```
2. В папку _infra_ скопируйте файлы `docker-compose.production.yml`
3. Создайте файл `.env` со следуищими переменными:
   ```
   POSTGRES_USER=... # имя пользователя БД
   POSTGRES_PASSWORD=... # пароль от БД
   POSTGRES_DB=django
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=... # секретный ключ django-проекта
   DEBUG='True'
   ALLOWED_HOSTS=... # <IP> 127.0.0.1 localhost <Домен>
   ```
4. Выполните команду `sudo docker compose -f docker-compose.production.yml up -d --buld`.
5. Выполните миграции `sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate`.
6. Создайте суперюзера `sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser`.
7. Соберите статику `sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic`
                    `sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/`

8. Заполните базу ингредиентами `sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_csv ingredients.csv`.
9. Создайте пару тегов в базе через админку.

### Автор: 
Python-разработчик
- [Смирнов Алексей](https://github.com/smalex02 "GitHub аккаунт")
