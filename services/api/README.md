# Brasaland Incidents API

Backend service for incidents analysis.

## Endpoints

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
