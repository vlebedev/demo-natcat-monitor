# Technical Specification — NatCat Event Monitor

## Project Context

This is a **demo application** showcasing autonomous multi-agent software development for a financial enterprise audience (P&C Reinsurance, NatCat specialty). The demo must be completed in **30-40 minutes** by **3 parallel Claude Code agents**.

---

## Non-Negotiable Principles

### 1. Simplicity First
- Prefer standard library solutions over external dependencies
- No complex build pipelines — the demo must "just work"
- Single language stack (Python) to minimize integration issues
- Each module must be testable independently

### 2. Clear Boundaries
- Three distinct concerns with minimal coupling:
  - **Domain Layer** — Pure business logic, no I/O, no UI
  - **Data Layer** — External API integration, data fetching
  - **UI Layer** — Streamlit presentation only
- Communication between layers via well-defined Python interfaces (dataclasses/Pydantic models)

### 3. Real Data, Mock Exposure
- Use **real** USGS Earthquake API for event data
- Use **mock** treaty/exposure data (JSON file or Python dict)
- No authentication required, no API keys needed

### 4. Demo-Friendly
- Visually clear output (maps, metrics, color-coded alerts)
- Fast startup time (< 5 seconds)
- Single command to run: `streamlit run app.py`
- Works offline for exposure data (only event fetch needs network)

---

## Technology Stack

### Core
- **Language:** Python 3.11+
- **UI Framework:** Streamlit (rapid prototyping, built-in components)
- **Maps:** Folium + streamlit-folium (Leaflet wrapper, no API key)
- **HTTP Client:** httpx (async support) or requests (simpler)
- **Data Validation:** Pydantic v2 (models with validation)

### Dependencies (requirements.txt)
```
streamlit>=1.28.0
streamlit-folium>=0.15.0
folium>=0.15.0
pydantic>=2.0.0
httpx>=0.25.0
```

### Development
- **Package Manager:** uv (with requirements.txt)
- **No Docker required** — direct execution
- **No database** — all state in memory or JSON files
- **No build step** — Streamlit runs Python directly

---

## Coding Standards

### Python General
- Type hints on all function signatures
- Pydantic models for all data structures crossing boundaries
- One module per concern
- No classes where functions suffice
- Docstrings on public functions (Google style)

### Module Rules
- `models.py` — Only Pydantic models, no logic
- `services.py` — Pure functions, no I/O, no Streamlit imports
- `data.py` — All external I/O (API calls, file reads)
- `app.py` — Streamlit UI only, imports from other modules

### Streamlit Conventions
- Use `st.columns()` for layout, not raw HTML
- Use `st.session_state` for any state that persists across reruns
- Use `@st.cache_data` for expensive computations (API calls)
- Keep UI code declarative — no complex logic in app.py

### Error Handling
- Fail fast with clear messages
- Use `st.error()` for user-facing errors
- Log exceptions but don't crash the app
- Provide fallback UI when data unavailable

---

## Testing Approach

Given the 30-40 minute constraint:
- **Unit tests** for domain logic only (`services.py`)
- **Manual testing** for UI and integration
- Tests in `tests/` folder using pytest
- No mocking of external APIs in initial implementation

---

## File Structure

```
demo-natcat-monitor/
├── src/
│   ├── __init__.py
│   ├── models.py        # Pydantic models (Event, Treaty, Alert)
│   ├── services.py      # Business logic (exposure calculation)
│   ├── data.py          # USGS API client, mock treaty loader
│   └── app.py           # Streamlit UI entry point
├── data/
│   └── treaties.json    # Mock treaty data
├── tests/
│   └── test_services.py # Unit tests for business logic
├── requirements.txt
└── README.md
```

---

## Interface Contracts

### Models (LeadDev defines, all use)
```python
class Earthquake(BaseModel):
    id: str
    magnitude: float
    latitude: float
    longitude: float
    place: str
    time: datetime
    depth_km: float

class Treaty(BaseModel):
    id: str
    name: str
    peril: str
    region: str
    latitude: float
    longitude: float
    radius_km: float
    limit_usd: int

class ExposureAlert(BaseModel):
    earthquake: Earthquake
    treaty: Treaty
    distance_km: float
```

### Data Functions (DataDev defines)
```python
def fetch_earthquakes(min_magnitude: float, days: int) -> list[Earthquake]: ...
def load_treaties() -> list[Treaty]: ...
```

### Service Functions (LeadDev defines)
```python
def calculate_distance_km(lat1, lon1, lat2, lon2) -> float: ...
def find_exposed_treaties(event: Earthquake, treaties: list[Treaty]) -> list[ExposureAlert]: ...
def summarize_exposure(alerts: list[ExposureAlert]) -> dict: ...
```

---

## Quick Start (for demo)

```bash
cd demo-natcat-monitor
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
streamlit run src/app.py
```
