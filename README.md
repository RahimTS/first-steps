# first-steps — FastAPI project skeleton

A minimal, modern FastAPI starter you can clone and build on. It includes:

- **FastAPI** app with a proper lifespan hook
- **MongoDB** via Motor (async) and GridFS bucket ready
- **Environment-based config** with `python-dotenv`
- **Structured settings** via a `dataclass`
- **CORS** enabled for rapid prototyping
- **uv** + `pyproject.toml` for fast, reproducible installs

---

## Tech stack
- **FastAPI** for the web framework
- **Uvicorn** as the ASGI server
- **Motor** for asynchronous MongoDB access
- **Loguru** for logging
- **dotenv** for `.env` loading
- **uv** for packaging/runtime (uses `pyproject.toml` + `uv.lock`)

---

## Project structure
```
.
├─ config/
│  └─ settings.py        # App settings from environment
├─ main.py               # FastAPI app entrypoint (lifespan connects to MongoDB)
├─ pyproject.toml        # Project metadata and dependencies
├─ uv.lock               # Reproducible lockfile for uv
├─ LICENSE
└─ README.md
```

---

## Requirements
- Python 3.9+
- A running MongoDB instance (local Docker or managed)
- Recommended: `uv` for dependency management

Install uv:
```bash
# Windows (PowerShell)
py -m pip install uv
# or
pip install uv
```

---

## Setup

### 1) Clone and enter the project
```bash
git clone <your-fork-or-template-url> first-steps
cd first-steps
```

### 2) Install dependencies
Using uv (recommended):
```bash
uv sync
```
This creates a virtual environment and installs dependencies from `pyproject.toml` and `uv.lock`.

Alternative with pip (if you don’t want uv):
```bash
python -m venv .venv
# PowerShell
. .venv\Scripts\Activate.ps1
# bash/cmd
source .venv/bin/activate  # or .venv\Scripts\activate on Windows cmd
pip install -e .
```

### 3) Configure environment
Create a `.env` file in the project root. Example:
```env
# App
APP_NAME=first-steps
DEBUG_MODE=true
ENV=local
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=first_steps_db
```
Settings are loaded in `config/settings.py`:
```python
# config/settings.py excerpt
@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "first-steps")
    debug_mode: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    env: str = os.getenv("ENV", "local")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = os.getenv("PORT", 8000)
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db: str = os.getenv("MONGO_DB")
```

---

## Run the app

Using uv (recommended):
```bash
uv run python main.py
```

Using pip/venv:
```bash
python main.py
```

The server starts with:
- Host: `HOST` (default `0.0.0.0`)
- Port: `PORT` (default `8000`)
- Reload: `DEBUG_MODE`

Open the interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## What’s included in `main.py`
- Lifespan startup/shutdown that:
  - Connects to MongoDB using `Motor`
  - Creates a `GridFSBucket` on the configured database
  - Logs connection/disconnection
- CORS middleware open to all origins for local dev
- Uvicorn runner configured from `settings`

---

## Extending the skeleton

### Add your first router
Create a `routers` package and a simple health endpoint.

```bash
mkdir -p routers
```

```python
# routers/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

Wire it into `main.py`:
```python
# main.py (excerpt)
from fastapi import FastAPI
from routers.health import router as health_router

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router)
```

### Access MongoDB from a route
During lifespan, the app attaches clients you can reuse:
```python
# main.py (excerpt)
app.mongo_client  # AsyncIOMotorClient
app.mongo_db      # AsyncIOMotorDatabase
app.mongodb_fs    # AsyncIOMotorGridFSBucket
```

In a route, you can get the app instance via `request.app`:
```python
from fastapi import APIRouter, Request

router = APIRouter(tags=["examples"])

@router.get("/items")
async def list_items(request: Request):
    db = request.app.mongo_db
    items = await db.items.find().to_list(length=100)
    return {"items": items}
```

### Configuration tips
- Use `.env` for local overrides; inject real secrets with your runtime (Docker/CI/CD)
- Split settings per environment if needed (e.g., `ENV=prod`)
- Tighten CORS for non-local environments

---

## Production notes
- Run with Uvicorn workers behind a reverse proxy (e.g., Nginx, Caddy):
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
- Configure structured logging and request IDs
- Add health/readiness endpoints for orchestration
- Pin and rotate dependencies (lockfile is included)

---

## Troubleshooting
- "Cannot connect to MongoDB": verify `MONGO_URI` and that MongoDB is reachable from your machine/container
- Windows PowerShell execution policy can block venv scripts; run PowerShell as Admin and set: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- If `uv` is not found after install, ensure the Python Scripts directory is on PATH

---

## License
This project is licensed under the terms of the LICENSE file in this repository.
