# RestWell

RestWell is a multi-tenant SaaS/PaaS platform for end-of-life and legacy services. The implementation follows the planning documents in `docs/`, starting with funeral parlor operations and expanding toward policy underwriters, cemetery operators, DHA integrations, and digital legacy tools.

## Local Development

Copy `.env.example` to `.env`, then start the backend dependencies and API:

```bash
make dev-up
```

Run backend tests:

```bash
make backend-test
```

Run Flutter tests after installing the Flutter SDK:

```bash
make flutter-test
```

## Current Sprint

Sprint 0 foundation is active: Django REST backend, JWT auth, tenant and branch models, custom user roles, Flutter admin login shell, Docker Compose, and CI.
