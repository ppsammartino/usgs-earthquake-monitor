.PHONY: build up down frontend logs migrate makemigrations createsuperuser test frontend-logs api-logs lint lint-py lint-fe fix_formatting

build:
	docker-compose build --no-cache

up:
	docker-compose up

down:
	docker-compose down

frontend:
	docker compose up frontend

logs:
	docker-compose logs -f

migrate:
	docker exec -it earthquake_monitor_api python manage.py migrate

makemigrations:
	docker exec -it earthquake_monitor_api python manage.py makemigrations

createsuperuser:
	docker exec -it earthquake_monitor_api python manage.py createsuperuser

test:
	docker-compose run --rm --no-deps api sh -c "python manage.py test"

frontend-logs:
	docker logs -f react_frontend

api-logs:
	docker logs -f earthquake_monitor_api

lint: lint-py lint-fe

lint-py:
	docker-compose run --rm --no-deps api sh -c "black --check /app && flake8 /app"

lint-fe:
	docker-compose run --rm --no-deps frontend yarn lint

fix_formatting:
	docker-compose run --rm api sh -c "/app/utils/fix__formatting.bash"