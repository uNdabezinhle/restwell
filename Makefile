.PHONY: dev-up dev-down backend-test backend-migrate backend-superuser flutter-test test

dev-up:
	docker compose up --build

dev-down:
	docker compose down

backend-migrate:
	cd backend && python manage.py migrate

backend-superuser:
	cd backend && python manage.py createsuperuser

backend-test:
	cd backend && python manage.py test

flutter-test:
	cd frontend/admin_app && flutter test
	cd frontend/client_app && flutter test

test: backend-test flutter-test
