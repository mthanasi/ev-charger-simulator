# EV Charger Simulator & Dashboard

A full-stack simulation tool to estimate energy demand, peak load, and concurrency for electric vehicle (EV) charging infrastructure.

## 📦 Features

- Simulate EV charging events with multiple charger types
- Calculate energy demand, peak load, and concurrency
- Visualize results in a dashboard with charts and tables
- Store simulation parameter sets and results in a database

## 🗂 Application Structure

```bash
ev-charger-simulator/
│
├── backend/           # fastapi service: simulation + crud api
│   ├── app/           # fastapi app
│   ├── packages/      # simulation package
│   ├── pyproject.toml
│   └── dockerfile
│
├── frontend/          # next.js 15 dashboard (react + tailwind)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   └── dockerfile
│
├── docker-compose.yml 
├── .env               
└── Makefile           # helper commands: dev / down / logs / sim
```

## 🚀 Quick Start

### 0. Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://formulae.brew.sh/formula/make)

### 1. Clone & spin up the full stack

```bash
git clone https://github.com/mthanasi/ev-charger-simulator.git
cd ev-charger-simulator
make build   
make up     
```

This spins up:

- FastAPI backend with CRUD API and openapi docs (on port 8000)
- Simulation CLI (in backend container)
- Postgres database (on port 5433)
- Next.js 15 UI (on port 3000) with recharts, tailwind, etc.

### 2. Makefile Commands

```bash
make help      # Show help message with all available commands
make build     # Build (or rebuild) all images
make up        # Start the stack in detached mode
make down      # Stop & remove containers (volumes survive)
make logs      # Tail all service logs
make sim       # Run the simulation CLI
make sim-help  # List every simulator CLI flag
```

Simulation CLI Flags:

```bash
--chargers     List of chargers in format 'NxP' where N is count and P is power in kW.
                Multiple chargers separated by comma (e.g. '5x11,3x22,1x50')
-m, --mult     Arrival-rate multiplier (default: 1.0)
--year         Year to simulate (for DST calculations, default: 2023)
--consumption  Vehicle energy consumption in kWh per 100km (default: 18.0)
--output       Output file for simulation results (JSON format)
--quick_test   Run a quick test with varying charger counts from 1 to 30
-s, --seed     Random seed for repeatable runs
```

Example:

```bash
make sim ARGS="-n 40 -m 1.25 -e 0.22 -p 22 -s 42"
```

## 📌 Environment Configuration

Copy `.env.example` to `.env` and edit the values:

```env
# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ev_charger_sim_db

# FRONTEND
NEXT_PUBLIC_API_URL=http://localhost:8000

# BACKEND
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5433/ev_charger_sim_db
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
DEBUG=TRUE

```

## 🧱 Components

Simulation Package

- Implements simulation as a CLI (`uv run simulator`)
- Returns: `energy_kWh`, `peak_load_kW`, `concurrency_factor`

CRUD API (FastAPI)

- Stores configurations parameters and simulation results
- Calculates metrics for each simulation result

Web App (Next.js 15)

- Recharts for power curves, histograms, etc.
- Styled with Tailwind CSS
- Form input and results view

## 🚧 Roadmap

- [ ] Add tests for the simulation package, CRUD API, and web app
- [ ] Relax the assumptions of the simulation package
- [ ] Add more metrics and visualizations to the web app
- [ ] TBD
