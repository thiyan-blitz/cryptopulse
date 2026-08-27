# CryptoPulse

A full-stack cryptocurrency trading simulator with real-time price streaming, portfolio management, and technical analytics — built to explore production-grade patterns for real-time data, authentication, and time-series storage.


---

## Overview

CryptoPulse lets users trade 10 major cryptocurrencies using a virtual balance, track portfolio performance with live P&L, and view technical indicators (RSI, SMA) computed from historical price data. Prices stream live from Binance's WebSocket API and are relayed to the frontend in real time.

## Features

- **Live price streaming** — real-time prices for 10 coins via Binance WebSocket, relayed to the frontend with sub-second latency
- **Authentication** — JWT access/refresh tokens, bcrypt password hashing, automatic silent token refresh on expiry
- **Trading engine** — buy/sell with live pricing, weighted average cost-basis tracking, real-time balance and holdings updates
- **Portfolio dashboard** — live portfolio value, per-holding P&L, and percentage returns
- **Transaction history** — filterable and sortable by coin, type, and time range
- **Technical analytics** — RSI (14) and SMA (20) computed from historical OHLC candles, visualized with interactive charts
- **Markets page** — live, sortable table of all supported coins

## Tech Stack

**Frontend:** React, React Router, Tailwind CSS, Recharts, Context API
**Backend:** FastAPI, async SQLAlchemy, Alembic, Pydantic
**Database:** PostgreSQL, TimescaleDB (hypertables for time-series price data)
**Real-time:** Binance WebSocket API, native FastAPI WebSockets
**Auth:** JWT (access + refresh token rotation), bcrypt

## Architecture

```
Binance WebSocket  →  FastAPI listener  →  in-memory price cache
                                          →  FastAPI WebSocket relay  →  React (live UI)

React  →  REST API (JWT-authenticated)  →  FastAPI routes  →  service layer  →  PostgreSQL / TimescaleDB
```

The backend follows a layered structure: routes handle HTTP/WebSocket concerns, services hold business logic (trade execution, analytics calculations), and SQLAlchemy models map to the database — keeping route handlers thin and logic independently testable.

## Database Design

10 relational tables (users, wallets, coins, holdings, transactions, watchlist, news, etc.) plus a TimescaleDB hypertable (`price_history`) for OHLC candle data, partitioned by time for efficient range queries at scale.

## Notable Engineering Details

- **Trade execution** always prices against the live in-memory cache (fed by the WebSocket listener), not a fresh API call — keeping fills fast and consistent for concurrent requests.
- **Cost basis** uses weighted-average accounting: buying more of a held coin recalculates `avg_buy_price` proportionally; selling leaves the remaining position's cost basis untouched, matching standard portfolio accounting.
- **Debugging story:** the initial WebSocket implementation subscribed to Binance's full all-symbol ticker stream (`!ticker@arr`), which connected successfully but silently dropped all data under certain network conditions. Isolated the issue with standalone scripts outside the FastAPI event loop, and resolved it by switching to a curated multi-symbol combined stream — which also better matched the app's actual needs (10 tracked coins, not thousands).
- **Auth resilience:** `apiFetch` on the frontend automatically retries a request once with a refreshed access token on a 401, falling back to a forced logout only if the refresh token itself has expired — avoiding unnecessary re-logins during normal use.

## Known Limitations / Future Work

- Historical candle data is populated via a one-time backfill rather than continuous live ingestion; a production deployment would stream ticks into TimescaleDB continuously and use continuous aggregates for real-time candle generation.
- Trading is simulated (virtual balance) rather than connected to a real exchange, by design — this keeps the project scoped to demonstrating full-stack trading logic without compliance/custody concerns.
- No Redis caching layer yet; live prices are cached in-process, which is sufficient for a single backend instance but wouldn't scale horizontally as-is.

## Running Locally

**Backend**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env    # fill in your own DB URL and secret keys
alembic upgrade head
python -m app.scripts.seed_coins
python -m app.scripts.backfill_price_history
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:5173`.
