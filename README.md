# Hajz (حجز)

An AI-powered stay booking platform built on real listings from 14 cities.
Guests get personalised recommendations and an AI assistant that turns
plain-language requirements into real, bookable stays.

> **Status:** design complete, database layer built. Live demo coming soon.

## Stack

| Layer | Technology |
|---|---|
| Frontend | Angular, Tailwind CSS |
| Backend | Flask, SQLAlchemy, Alembic, Marshmallow |
| Database | MySQL 8 (local, Docker) / TiDB Cloud Serverless (production) |
| ML | scikit-learn, embeddings, offline batch pipeline |
| AI | Gemini (tool calling) |
| Payments | Stripe (test mode only) |
| Hosting | Vercel, Render, GitHub Actions |

## Documentation

| Document | Contents |
|---|---|
| [01 Planning](docs/01-planning.md) | Vision, scope, requirements, milestones |
| [02 Architecture](docs/02-architecture.md) | System design, key flows, security |
| [03 Data model](docs/03-data-model.md) | Tables, relationships, sizing |
| [04 Business rules](docs/04-business-rules.md) | Booking, pricing, cancellation and other rules |

## Run the database locally

Requirements: Python 3.13, Docker Desktop.

```powershell
docker compose up -d
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed
python manage.py db-status
```

## Data

Listing data comes from [Inside Airbnb](https://insideairbnb.com/), licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Photos are licensed
images matched by city and room type, not photos of the actual properties.
Payments run in Stripe test mode; no real money is charged.
