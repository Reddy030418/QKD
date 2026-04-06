# QDP-SAE v1 Scope and API Contract Freeze

Last updated: 2026-04-06
Status: Frozen for Phase 0

## Scope (v1)
- Secure JWT auth with refresh-token flow.
- Role-based access control with `admin` and `user` roles.
- Protected QKD run + session APIs.
- Analytics summary/trends/user endpoints.
- WebSocket channel for session progress and final result.

## Auth Contract
- `POST /auth/register`
  - Request: `{ "username": "str", "email": "str", "password": "str" }`
  - Response: `{ "message": "...", "user": { "id": int, "username": "str", "email": "str", "role": "admin|user" } }`
- `POST /auth/login`
  - Request: `{ "username": "str", "password": "str" }`
  - Response: `{ "access_token": "str", "refresh_token": "str", "token_type": "bearer", "user": { ... } }`
- `POST /auth/refresh`
  - Request: `{ "refresh_token": "str" }`
  - Response: `{ "access_token": "str", "token_type": "bearer" }`
- `POST /auth/logout` (protected)
  - Response: `{ "message": "Successfully logged out" }`
- `GET /auth/me` (protected)
  - Response: `{ "id": int, "username": "str", "email": "str", "role": "admin|user", "is_active": bool }`

## QKD Contract
- `POST /qkd/run` (protected)
  - Request: `{ "key_length": int[10..500], "noise_level": float[0..30], "detector_efficiency": float[70..100], "eavesdropper_present": bool }`
  - Response: session payload including `session_id`, protocol vectors, `stats`, `error_rate`, `security_status`.

## Sessions Contract
- `GET /sessions` (protected)
  - User: own sessions only.
  - Admin: all sessions, optional `user_id` filter.
- `GET /sessions/{session_id}` (protected)
  - Owner or admin only.
- `DELETE /sessions/{session_id}` (protected)
  - Owner or admin only.
- `GET /sessions/stats/summary` (protected)
  - User-scoped for users, global for admins.

## Analytics Contract
- `GET /analytics/summary` (protected)
- `GET /analytics/trends?days={1..365}` (protected)
- `GET /analytics/user/{id}` (protected)
  - Admin: any user.
  - User: own id only.

## WebSocket Contract
- `WS /ws/qkd` and `WS /qkd/ws`
- Message types:
  - client -> server: `subscribe`, `unsubscribe`, `ping`
  - server -> client: `qkd_progress`, `qkd_result`, `status`, `pong`, `error`

## Non-goals for v1
- Distributed queues (Kafka), Redis caching, and CI/CD pipelines.
- Multi-tenant org model.
- Production-grade token revocation store beyond token-version invalidation.
