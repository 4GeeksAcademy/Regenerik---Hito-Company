# Brasaland Incidents API

Backend service for incidents analysis and supplier directory management.

Stack for supplier directory: FastAPI + TinyDB + Pydantic.

## Endpoints

### Suppliers directory (lightweight storage)

- `GET /suppliers`
  - Optional query filters: `country`, `category`, `status`.
  - Returns `{ "items": [...], "total": number }`.

- `GET /suppliers/{supplier_id}`
  - Returns supplier details by ID.
  - Returns `404` when not found.

- `POST /suppliers`
  - Creates a supplier.
  - Invalid payloads are rejected with `422` by FastAPI/Pydantic validation.
  - Validates business rules from the company context:
    - `country` must be `Colombia` or `USA`.
    - `currency` must match country (`COP` for Colombia, `USD` for USA).
    - `categories` must contain one or more valid values.

- `PATCH /suppliers/{supplier_id}/rate`
  - Updates `rate_per_unit` and refreshes `updated_at` timestamp.

- `PATCH /suppliers/{supplier_id}/status`
  - Sets `status` to `active` or `suspended`.

- `DELETE /suppliers/{supplier_id}`
  - Deletes a supplier (for data correction scenarios).

- `POST /api/incidents/analyze`
  - `multipart/form-data` with field `file` (`.csv`)
  - Runs the incidents validation + metrics logic and returns JSON summary.

- `GET /api/incidents/results/export`
  - Returns the latest analysis as downloadable `results.csv`.

- `GET /api/incidents/results/latest`
  - Returns latest analysis JSON summary.

- `GET /health`
  - Healthcheck.

## Run

```bash
cd services/api
python3 -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Supplier data is persisted in TinyDB at `services/api/data/suppliers.json`.
On first run, the file is auto-seeded with the Brasaland suppliers set.

## Seeder

- Script: `services/api/seed.py`
- Run: `uv run seed` (from `services/api`)
- Behavior: inserts only missing suppliers (no duplicates) and prints inserted/skipped counts.
