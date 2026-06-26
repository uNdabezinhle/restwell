# RestWell

**The Modern Platform for End-of-Life & Legacy Services**

RestWell is a multi-tenant SaaS/PaaS platform designed to digitize and connect the entire end-of-life ecosystem — starting with funeral parlors and expanding into cemetery management, insurance underwriting, government services (DHA), and digital legacy tools.

## Vision

To become the leading digital operating system for dignified end-of-life services in Africa and beyond — giving every funeral business, family, and stakeholder modern, compliant, and branded tools.

## Key Features (v1)

- Multi-tenant & multi-branch architecture
- Full funeral case & family management
- Custom funeral policy engine with multiple underwriters
- Mortuary operations module (independent service)
- Geolocation & field tracking (independent service)
- **Custom Branding Engine** (white-labeling)
- **Branded Client Mobile App** generation (Android first)
- **Client Website Builder** with domain management
- Strong compliance foundation (POPIA, FSCA-ready)
- Cross-platform (Flutter): Web, Mobile, Desktop
- Offline-first support for South African realities

## Tech Stack

**Backend**
- Python 3.12 + Django + Django REST Framework
- PostgreSQL
- Celery + Redis (for background tasks)
- Docker

**Frontend**
- Flutter (Web + Mobile + Desktop)
- Riverpod / Bloc for state management

**Infrastructure**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- Self-hostable or cloud deployment

## Project Structure (Monorepo)

```
restwell/
├── backend/                 # Django Project
│   ├── config/             # Django settings
│   ├── tenants/            # Multi-tenant core
│   ├── cases/              # Case & Family management
│   ├── policies/           # Funeral policies + Underwriters
│   ├── financials/         # Invoicing & Payments
│   ├── inventory/          # Inventory management
│   ├── scheduling/         # Calendar & Bookings
│   ├── branding/           # Custom Branding Engine
│   ├── website_builder/    # Client Website Builder
│   ├── geolocation/        # Geolocation Service (independent)
│   ├── mortuary/           # Mortuary Module (independent)
│   └── ...
├── frontend/               # Flutter Project
│   ├── admin_app/          # Main admin/staff app
│   └── client_app/         # Client-facing app (can be branded)
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

## Getting Started (Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Flutter SDK

### Quick Start

```bash
# Clone the repository
git clone https://github.com/uNdabezinhle/restwell.git
cd restwell

# Start all services
make dev-up

# Or manually with Docker Compose
docker-compose up --build
```

## Development Roadmap

See the detailed [Master Sprint Overview](./docs/sprints/Master_Sprint_Overview.md) for the full 11-sprint plan to v1.

### Current Focus
- **Sprint 0**: Foundation & Multi-tenant Architecture
- **Sprint 1**: Core Case Management
- **Sprint 5 & 7**: Key Differentiators (Branding + Branded App)

## Contributing

This project is currently in active development by the founder. Contributions and feedback are welcome once the core MVP stabilizes.

## License

Proprietary (All rights reserved)

## Contact

**Founder**: Ndabezinhle (uNdabezinhle)  
**Location**: Johannesburg, South Africa  
**X**: [@uNdabezinhle](https://x.com/uNdabezinhle)

---

**RestWell** — Dignity. Legacy. Peace of Mind.