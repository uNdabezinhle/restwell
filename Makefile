.PHONY: dev-up dev-down admin-up client-up frontend-admin-up frontend-admin-test backend-test test-backend backend-migrate backend-superuser seed-demo flutter-test test-flutter test

dev-up:
	docker compose up --build

dev-down:
	docker compose down

frontend-admin-up:
	docker compose up admin_frontend

admin-up:
	docker compose up admin_frontend

client-up:
	docker compose up client_frontend

frontend-admin-test:
	docker compose run --rm admin_frontend flutter test

backend-migrate:
	cd backend && python manage.py migrate

backend-superuser:
	cd backend && python manage.py createsuperuser

backend-test:
	cd backend && python manage.py test

test-backend: backend-test

seed-demo:
	cd backend && python manage.py seed_demo

flutter-test:
	docker compose run --rm admin_frontend flutter test

test-flutter:
	docker compose run --rm admin_frontend flutter test
	docker compose run --rm client_frontend flutter test

test: backend-test flutter-test
