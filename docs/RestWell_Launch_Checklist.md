# RestWell V1 Launch Checklist

## Environment

- Set `DJANGO_DEBUG=false` and rotate `DJANGO_SECRET_KEY`.
- Configure `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` for production domains.
- Enable `SECURE_SSL_REDIRECT`, secure cookies, and HSTS after HTTPS is confirmed.
- Use managed PostgreSQL and Redis; do not use local container credentials in production.

## Release Validation

- Run `python manage.py test`.
- Run `docker compose config --quiet`.
- Confirm `/api/health/live/` and `/api/health/ready/` return healthy responses.
- Confirm tenant admins cannot see data from another tenant.
- Validate branded website preview and app build request flow for one pilot tenant.

## Monitoring

- Capture API logs from stdout.
- Alert on repeated `5xx` responses, failed login spikes, readiness failures, and database connection errors.
- Review onboarding task completion for every pilot tenant before go-live.

## Launch Day

- Create production super admin and tenant admin accounts.
- Import starting tenants, branches, users, policy templates, and inventory.
- Confirm backups and restore procedure.
- Keep the pilot support channel open during the first live case workflow.
