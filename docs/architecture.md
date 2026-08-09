# HMIE System Architecture & Workflow 🏛️

This 1-page document outlines the clean, single-ownership architecture of the **Historical Market Intelligence Engine (HMIE)**.

---

## 🧭 Single Ownership Rule

Every dashboard page in HMIE is owned by exactly **one Router**, which calls **one Service**, which queries **Oracle Database**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          HMIE Web Dashboards                            │
│                  (HTML Pages in /dashboards Directory)                  │
└───────┬──────────────┬──────────────┬──────────────┬──────────────┬─────┘
        │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  home.html   ││  rbi.html   ││  festival_   ││ benchmark_   ││   system_    │
│              ││              ││ research.html││comparison.html│  health.html │
└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘
        │               │               │               │               │
        ▼               ▼               ▼               ▼               ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│system_router ││  rbi_router  ││evidence_router││compare_router││system_router │
└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘
        │               │               │               │               │
        ▼               ▼               ▼               ▼               ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│health_service││analog_service││  research_   ││ analytics_   ││health_service│
│              ││ rbi_service  ││summary_service││    engine    ││              │
└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘
        │               │               │               │               │
        └───────────────┴───────┬───────┴───────────────┴───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Oracle Database Connection                         │
│                    (core/database.py Connection)                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Layer Responsibilities

### 1. `dashboards/` (Presentation Layer)
- HTML files providing a clean, dark-theme visual workspace.
- **Strict Rule**: No inline duplicated HTML. Pages resolve API calls relative to the server host.

### 2. `routers/` (HTTP Gateway Layer)
- Maps REST API requests (`/api/v1/...`) to service methods.
- Validates request payloads and query parameters using Pydantic models.

### 3. `services/` (Business Logic Layer)
- Contains all quantitative math, historical calculations, similarity scoring, and narrative generation.
- **Strict Rule**: No UI code or HTTP handling in services.

### 4. `core/` (Infrastructure Layer)
- Infrastructure strictly limited to Oracle DB connection pooling (`database.py`), global configuration (`config.py`), cryptographic execution hashing (`governance.py`), and schemas (`intent_schema.py`).
