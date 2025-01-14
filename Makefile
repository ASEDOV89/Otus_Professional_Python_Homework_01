.PHONY: build up down test lint coverage run

build:
	docker build -t homework_01 .

up:
	docker-compose up -d

down:
	docker-compose down

test:
	poetry run pytest tests/

lint:
	poetry run flake8 src/ tests/

run:
	poetry run python src/main.py
