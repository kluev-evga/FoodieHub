# Продуктовый помошник

[![python version](https://img.shields.io/static/v1?label=Python&message=3.10.6&color=97ca00&style=for-the-badge)](https://python.org)
[![django version](https://img.shields.io/static/v1?label=DJANGO&message=4.2.2&color=77ca00&style=for-the-badge)](https://www.djangoproject.com/)
[![drf version](https://img.shields.io/static/v1?label=DRF&message=3.14.0&color=97ca00&style=for-the-badge)](https://www.django-rest-framework.org/)
![api version](https://img.shields.io/static/v1?label=API%20VERSION&message=1.0.0&color=77ca00&style=for-the-badge)
[![licence](https://img.shields.io/static/v1?label=LICENSE&message=MIT&color=97ca00&style=for-the-badge)](https://github.com/kluevEVGA/api_final_yatube/blob/master/LICENSE)

## О ПРОЕКТЕ

Cайт Foodgram, «Продуктовый помощник».  
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять
понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых
для приготовления одного или нескольких выбранных блюд.

## ЗАПУСК ПРОЕКТА

<hr/>
<details close>
<summary><h4 style="display: inline">WINDOWS <h3 style="display: inline">▶️</h3></h4></summary>

_Клонировать проект_

```shell
https://github.com/kluev-evga/foodgram-project-react.git
```

_Установить локальное окружение_

```shell
python -m venv venv
```

_Активировать окружение_

```shell
venv\Scripts\activate # PowerShell
```

```shell
source venv/Scripts/activate # Git Bash(Bash)
```

_Установить зависимости_

```shell
pip install -r requirements.txt
```

_Перейти в папку с проектом_

```shell
cd .\backend\
```

_Выполнить миграции_

```shell
python3 manage.py migrate
```

_запустить сервер_

```shell
python3 manage.py runserver
```

</details>
<hr/>

<details close>
<summary><h4 style="display: inline">LINUX & MacOS<h3 style="display: inline">▶️</h3></h4></summary>

_Клонировать проект_

```shell
https://github.com/kluev-evga/foodgram-project-react.git
```

_Установить локальное окружение_

```shell
python3 -m venv venv
```

_Активировать окружение_

```shell
source venv/bin/activate
```

_Установить зависимости_

```shell
pip install -r requirements.txt
```

_Перейти в папку с проектом_

```shell
cd .\backend\
```

_Выполнить миграции_

```shell
python3 manage.py migrate
```

_запустить сервер_

```shell
python3 manage.py runserver
```

</details>
<hr/>

## Добавление данных из csv или json

```shell
python3 manage.py csv
python3 manage.py json
```

<details close>
<summary><h3 style="display: inline">Настройка SSL сертификата <h2 style="display: inline"> 🚧</h2></h3></summary>


<br/>

### Docker

```yaml
nginx:
  ...
  ports:
    - "80:80"
    - "443:443"
  volumes:
    ...
    - ./certbot/www:/var/www/certbot/
    - ./certbot/conf/:/etc/nginx/ssl/

certbot:
  image: certbot/certbot:latest
  volumes:
    - ./certbot/www/:/var/www/certbot/
    - ./certbot/conf/:/etc/letsencrypt/
```

<br/>

### Создаем файл конфигурации nginx.conf

`не забываем указать свои dns`

```cfgrlanguage
server {

    listen 80;
    listen [::]:80;
    server_name foodgram-project.dynnamn.ru www.foodgram-project.dynnamn.ru;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://foodgram-project.dynnamn.ru$request_uri;
    }
}
```

<br/>

### Запускаем команду, чтобы заполнить папку сертификатов:

`не забываем указать свои dns`

```shell
sudo docker compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d example.com
```

<br/>

### Теперь, когда нас есть сертификаты, можно заполнить блок 443:

`не забываем указать свои dns`  
После обновления nginx.conf необходимо перезапустить контейнер nginx

```cfgrlanguage
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://foodgram-project.dynnamn.ru$request_uri;
    }
}

server {
    listen 443 default_server ssl http2;
    listen [::]:443 ssl http2;
    server_name example.org;
    ssl_certificate /etc/nginx/ssl/live/example.org/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/example.org/privkey.pem;

    location / {
    	# ... заполняем все необходимые пути
    }
}
```

### Обновление сертификата

```shell
sudo docker compose run --rm certbot renew
```

### подробнее:

https://dvsemenov.ru/nastrojka-https-s-pomoshhyu-nginx-lets-encrypt-i-docker/

</details>

## ЛИЦЕНЗИЯ

Распространяется по `MIT` лицензии. Для дополнительной информации
смотри: [LICENSE](https://github.com/kluevEVGA/foodgram-project-react/blob/master/LICENSE)