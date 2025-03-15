
# **_Foodgram_**
Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать свои собственные рецепты, обмениваться ими с другими пользователями, подписываться на них и оформлять собственный список продуктов в удобном текстовом файле. И это не все!


### _Развернуть проект на удаленном сервере:_

**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**_Скопировать на сервер файлы docker-compose.yml:_**
```
sudo nano docker-compose.yml
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
```
sudo docker compose up -d
```
**_Выполнить миграции:_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных содержимым из файла ingredients.json:_**
```
sudo docker compose exec backend python manage.py load_ingredients
```
**_Создать суперпользователя:_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```

### Автор

Норенко Евгений 
norugin@gmail.com
