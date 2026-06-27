.PHONY: dev-up dev-down frontend-admin-up frontend-admin-test backend-test backend-migrate backend-superuser flutter-test test

dev-up:
	docker compose up --build

dev-down:
	docker compose down

frontend-admin-up:
	docker compose up admin_frontend

frontend-admin-test:
	docker compose run --rm admin_frontend flutter test

backend-migrate:
	cd backend && python manage.py migrate

backend-superuser:
	cd backend && python manage.py createsuperuser

backend-test:
	cd backend && python manage.py test

flutter-test:
	docker compose run --rm admin_frontend flutter test

test: backend-test flutter-test
