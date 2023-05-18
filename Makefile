#!make

e=.env
f=-f docker-compose.backend.yml
PYTHON_BACKEND=itpro72.ru:5050/strana-artw/strana-backend/python-backend:latest
PYTHON_CABINET=itpro72.ru:5050/strana-artw/strana-backend/python-cabinet:latest
PYTHON_ADMIN=itpro72.ru:5050/strana-artw/strana-backend/python-admin:latest

config:
	docker-compose $(f) --env-file $(e) config

build:
	docker-compose $(f) --env-file $(e) build  $(c)

build_backend:
	docker-compose $(f) --env-file $(e) build --build-arg PYTHON_BACKEND=$(PYTHON_BACKEND) backend

build_cabinet:
	docker-compose $(f) --env-file $(e) build --build-arg PYTHON_CABINET=$(PYTHON_CABINET) cabinet

build_admin:
	docker-compose $(f) --env-file $(e) build --build-arg PYTHON_ADMIN=$(PYTHON_ADMIN) admin
up:
	docker-compose $(f) --env-file $(e) up -d $(c)

restart:
	docker-compose $(f) --env-file $(e) restart $(c)

sh:
	docker-compose $(f) --env-file $(e) exec -ti $(c) sh

run:
	docker-compose $(f) --env-file $(e) run $(c)

mm:
	docker-compose $(f) --env-file $(e) exec $(c) python manage.py makemigrations

ps:
	docker-compose $(f) --env-file $(e) ps

logs:
	docker-compose --env-file $(e) logs $(c)


