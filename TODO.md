# QDP-SAE Upgrade TODO

## Phase 0 - Foundation (Start Here)
- [x] Finalize PRD scope and freeze v1 endpoints/contracts
- [x] Create `.env.example` with security-focused defaults
- [x] Add centralized settings validation for auth, DB, CORS, and token expiry
- [x] Add structured logging baseline for API, auth, and simulation events

## Phase 1 - Authentication & Authorization (JWT + RBAC)
- [x] Add secure password hashing using `passlib[bcrypt]`
- [x] Implement `POST /auth/register` with role assignment rules
- [x] Implement `POST /auth/login` returning `access_token` + `refresh_token`
- [x] Implement `POST /auth/refresh` for token rotation
- [x] Implement logout/token invalidation strategy
- [x] Add `get_current_user` dependency to protected routes
- [x] Add role-based guard (`admin`, `user`) with reusable dependency
- [x] Restrict admin-only operations (global analytics, cross-user queries, delete)

## Phase 2 - Data Pipeline Refactor (ETL-Oriented)
- [x] Ingestion layer: validate and normalize simulation inputs via Pydantic
- [x] Processing layer: isolate BB84 simulation engine from router logic
- [x] Add step-level events for bit generation, transmission, sifting, final key
- [x] Transformation layer: compute QBER, key rate, security status consistently
- [x] Storage layer: persist session parameters, outputs, metrics, and user ownership
- [x] Serving layer: return stable response DTOs for frontend consumption

## Phase 3 - Secure API Surface
- [x] Protect `POST /qkd/run`
- [x] Make `GET /sessions` user-scoped by default
- [x] Add `GET /sessions/{id}` with ownership/admin checks
- [x] Harden `/dashboard` and analytics endpoints with JWT auth
- [x] Add request/response schemas for all critical routes

## Phase 4 - Analytics Engine
- [x] Implement `GET /analytics/summary`
- [x] Implement `GET /analytics/trends` (QBER over time + key rate trends)
- [x] Implement `GET /analytics/user/{id}` (admin/global, user/self)
- [x] Add derived metrics: secure ratio, compromise ratio, noise-error correlation
- [x] Add efficient DB queries and pagination/date filters

## Phase 5 - Real-Time Simulation Upgrade
- [x] Replace fake progress UI with WebSocket-driven progress updates
- [x] Stream protocol stages: generation, transmission, sifting, completion
- [x] Add frontend WebSocket client lifecycle handling + reconnect policy
- [x] Correlate WebSocket messages by `session_id`

## Phase 6 - Frontend Modernization
- [x] Refactor auth context to store access + refresh tokens
- [x] Add axios interceptor for auth headers and refresh retry
- [x] Implement route guards (public/private/admin)
- [x] Update dashboard charts to consume new analytics APIs
- [x] Improve session history filters/search and secure-only views
- [x] Add auth/session expiry UX handling

## Phase 7 - Security Hardening
- [x] Tighten CORS to environment-driven allowlist
- [x] Add optional rate limiting for auth and simulation routes
- [x] Enforce strong input validation and error hygiene
- [x] Remove debug credential paths and insecure fallback code
- [x] Add audit logging for login, refresh, logout, and privileged actions

## Phase 8 - Quality, Testing, and Release
- [ ] Unit tests: auth service, token lifecycle, RBAC guards
- [ ] Integration tests: auth -> qkd run -> sessions -> analytics flow
- [ ] Frontend tests for auth flows and protected routing
- [ ] Add Docker/dev/prod configuration checks
- [ ] Prepare release notes and deployment checklist

## Stretch Goals
- [ ] PostgreSQL migration + Alembic migrations
- [ ] Redis for token/session cache and rate limiting
- [ ] Kafka-based simulation event stream
- [ ] CI/CD with lint, test, build, and deploy gates

## In Progress Now
- [x] Phase 1 backend implementation (secure JWT auth + RBAC)
- [x] Phase 3 API protection for QKD/sessions/analytics
- [x] Phase 4 initial analytics endpoints
