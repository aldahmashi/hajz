# Hajz (حجز) — Project Plan

| | |
|---|---|
| Version | 1.0 (approved) |
| Date | 2026-10-16 |
| Owner | aldahmashi |
| Status | Planning complete → Design in progress |

## 1. Vision

**Hajz** is a live, AI-powered stay booking platform built on real listings from
14 cities worldwide. Guests get personalised recommendations and an AI assistant
that turns plain-language requirements into real, bookable stays.

The project is a portfolio piece: it must be **publicly live, free to run, and
demonstrate production-grade engineering** (booking integrity, ML, LLM tool use,
CI/CD).

### Success criteria

| # | Criterion |
|---|---|
| S1 | Publicly live; anyone can register and complete a test booking |
| S2 | A recruiter can see the key features in under 60 seconds via a demo persona |
| S3 | Recommender beats a popularity baseline on precision@10 (offline evaluation) |
| S4 | p95 API latency < 500 ms when the backend is warm |
| S5 | CI runs tests and lint on every push; failed checks block deployment |
| S6 | Running cost: $0 / month |

## 2. Scope

**In scope:** authentication, catalogue and search, map, booking with Stripe test
payments, wishlist, reviews, recommendations, AI assistant, transactional
email, admin dashboard, CI/CD, monitoring.

**Out of scope (documented as future work):** real payments and payouts, host
onboarding and management, guest–host messaging, dynamic pricing, channel
managers / GDS, native mobile apps, internationalisation.

## 3. Users and roles

| Role | Description |
|---|---|
| Visitor | Not logged in. Browse, search, map, limited AI assistant |
| Guest | Registered. Adds booking, wishlist, reviews, personalised recommendations |
| Demo persona | Pre-seeded guest with history; one-click login for recruiters |
| Admin | Metrics, users, bookings, ML job status, recommender evaluation |
| Host | Imported from data only; no login |

## 4. Functional requirements

Priority uses MoSCoW: **M**ust, **S**hould, **C**ould.

### AUTH — Accounts
| ID | Requirement | P |
|---|---|---|
| AU-1 | Register with email and password, protected by Cloudflare Turnstile | M |
| AU-2 | Email verification | M |
| AU-3 | Login / logout with short-lived access token and rotating refresh token | M |
| AU-4 | Forgot / reset password | M |
| AU-5 | One-click demo persona login | M |
| AU-6 | Delete my account and data | S |
| AU-7 | Google sign-in | C |

### CAT — Catalogue and search
| ID | Requirement | P |
|---|---|---|
| CA-1 | Browse 14 cities | M |
| CA-2 | Search by city, dates, guests, price, room type, amenities; sort; paginate | M |
| CA-3 | Map view synced with result list (OpenStreetMap / Leaflet) | M |
| CA-4 | Listing page: photos, description, amenities, host, location, availability calendar, reviews | M |
| CA-5 | Semantic search ("quiet place for remote work") | S |
| CA-6 | Display prices in the user's chosen currency | S |

### BKG — Booking
| ID | Requirement | P |
|---|---|---|
| BK-1 | Price quote: nights × rate + cleaning + service fee + tax | M |
| BK-2 | Hold dates for 10 minutes → confirm on payment, or expire | M |
| BK-3 | No double booking under concurrent requests (enforced by the database) | M |
| BK-4 | Stay rules: min/max nights, max guests | M |
| BK-5 | Payment via Stripe **test mode** (no real money) | M |
| BK-6 | Cancellation with refund calculated by policy | M |
| BK-7 | "My trips" with status: held, confirmed, completed, cancelled, expired | M |
| BK-8 | Auto-complete bookings after check-out | S |

### WR — Wishlist and reviews
| ID | Requirement | P |
|---|---|---|
| WR-1 | Save / unsave stays | M |
| WR-2 | Review after a completed stay, one per booking | S |

### REC — Recommendations
| ID | Requirement | P |
|---|---|---|
| RE-1 | "Similar stays" on listing page | M |
| RE-2 | "For you" on home page, popularity fallback for new users | M |
| RE-3 | "Guests also stayed at" | M |
| RE-4 | "Why this?" explanation per recommendation | S |
| RE-5 | Cross-city taste matching | S |
| RE-6 | Nightly batch rebuild with evaluation report | M |

### AI — Assistant (Gemini)
| ID | Requirement | P |
|---|---|---|
| AI-1 | Chat that turns requirements into real, bookable stay cards | M |
| AI-2 | Grounded answers only, via tool calling against our API | M |
| AI-3 | Daily quota per user / IP; refuses off-topic requests | M |
| AI-4 | Falls back to standard search when Gemini is unavailable | M |
| AI-5 | Conversation memory within a session | S |
| AI-6 | Answers review questions ("is it noisy?") with quoted sources | S — phase 2 |
| AI-7 | Review insights per listing ("Guests love… / Watch out…") | S — phase 2 |

### NOT — Email
| ID | Requirement | P |
|---|---|---|
| NO-1 | Verification, password reset, booking confirmed, booking cancelled | M |

### ADM — Admin
| ID | Requirement | P |
|---|---|---|
| AD-1 | Dashboard: users, bookings, recommender metrics, ML job runs | S |

### DATA — Data pipeline
| ID | Requirement | P |
|---|---|---|
| DA-1 | Import and clean Inside Airbnb data, ≤ 500 stays per city | M |
| DA-2 | Currency normalisation (USD base) and per-city time zones | M |
| DA-3 | Assign licensed Pexels / Unsplash photos with attribution | M |
| DA-4 | Generate embeddings for all stays | M |
| DA-5 | Generate demo personas with interaction history | M |
| DA-6 | Nightly job: clean expired holds and junk data, rebuild recommendations | M |

## 5. Non-functional requirements

| Area | Requirement |
|---|---|
| Performance | p95 < 500 ms warm; recommendations served from a precomputed table |
| Availability | UptimeRobot monitoring; free-tier cold start accepted with a "waking up" screen |
| Security | Argon2 password hashing, short-lived JWTs, rate limiting, Turnstile, strict CORS, secrets in env vars only, OWASP Top 10 awareness, Gemini key server-side only |
| Privacy | Minimal personal data; account deletion; notice that the assistant uses Gemini's free tier |
| Cost | $0 / month |
| Quality | Automated tests with ≥ 70 % coverage of backend core; ruff lint; CI gate |
| Observability | Structured logs with request IDs; Sentry (free tier) for errors |
| Portability | Docker + env-var config; documented migration path between hosts |
| Usability | Responsive (mobile first); basic accessibility (contrast, keyboard, alt text) |

## 6. Constraints and assumptions

- Backend: Flask (adapted from the CTI foundation). Frontend: Angular. Database: MySQL-compatible (TiDB Cloud Serverless in production, MySQL 8 locally).
- Code: public GitHub monorepo `aldahmashi/hajz`. CI/CD: GitHub Actions.
- Listing data is a fixed snapshot (Inside Airbnb, September 2026). Availability is partly generated. Photos are licensed images matched by city and room type, not the actual property.
- Free tiers may change; the design must keep host migration cheap.

## 7. Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Inside Airbnb data, imported once | Free, no runtime dependency, real behaviour data for the recommender |
| D2 | Pexels / Unsplash photos | Licensed and permanent |
| D3 | Gemini behind a provider interface | Free tier; swappable |
| D4 | Batch-precomputed recommendations | Fits free-tier memory; fast reads |
| D5 | Own JWT authentication | Public app, not limited to APU accounts |
| D6 | Deploy on day one | Lower risk; learn deployment incrementally |
| D7 | Stripe test mode | Realistic payment flow and webhooks with no real money |
| D8 | Single public monorepo | Easier for recruiters; one CI pipeline |

## 8. Data

**Source:** [Inside Airbnb](https://insideairbnb.com/get-the-data/) — licensed
under Creative Commons Attribution 4.0 (CC BY 4.0). Attribution is shown in the
app footer and the README.

**Cities (14, up to 500 stays each, ≈ 7,000 stays):**

| Region | Cities |
|---|---|
| Asia | Tokyo, Bangkok, Singapore, Taipei |
| Europe / Middle East | Istanbul |
| Europe | London, Paris, Barcelona, Rome |
| Americas | New York City, Mexico City, Rio de Janeiro |
| Africa | Cape Town |
| Oceania | Sydney |

Selection rule per city: active listings with valid price and coordinates,
ranked by review count, top 500.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Free tier changes or ends | Docker + env vars; documented migration runbook |
| Gemini quota exhausted | Fallback search; per-user quotas |
| Spam / abuse on public sign-up | Turnstile, rate limits, nightly cleanup |
| Scope creep | Strict MoSCoW; phase 2 only after core is live |
| Data licence | CC BY 4.0 attribution in app and README |
| First-time deployment | Deploy "hello world" first; step-by-step runbook |
| Cross-site cookies (Vercel ↔ Render) | Same-origin API proxy via Vercel rewrites (see architecture) |

## 10. Milestones

Every milestone ends **live in production**.

| # | Milestone | Outcome |
|---|---|---|
| M0 | Setup | Repo, Docker, CI, "hello world" live on Render + Vercel + TiDB |
| M1 | Data | Cities imported, photos assigned, embeddings generated |
| M2 | Catalogue | Search, filters, map, listing page |
| M3 | Accounts | Register, verify, login, demo personas |
| M4 | Booking | Quote, hold, Stripe test payment, confirm, cancel, my trips |
| M5 | Recommender | Batch job, all recommendation types, evaluation page |
| M6 | AI assistant | Gemini tool calling, quotas, fallback |
| M7 | Polish | Admin dashboard, Sentry, README, demo video, phase 2 features |

## 11. Accounts needed (owner action)

GitHub (have), Render, Vercel, TiDB Cloud, Stripe (test mode), Resend,
Google AI Studio (Gemini key), Cloudflare (Turnstile), Pexels / Unsplash API,
Sentry, UptimeRobot. Each will be set up with a guide when its milestone starts.
