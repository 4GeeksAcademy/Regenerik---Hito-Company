# API de Incidencias Brasaland

Servicio backend para análisis de incidencias.

## Endpoints

- `POST /api/incidents/analyze`
  - Recibe `multipart/form-data` con el campo `file` (`.csv`).
  - Ejecuta la misma lógica de validación + métricas y devuelve resumen en JSON.

- `GET /api/incidents/results/export`
  - Devuelve el último análisis como `results.csv` descargable.

- `GET /api/incidents/results/latest`
  - Devuelve el último resumen en JSON.

- `GET /health`
  - Healthcheck.

## Ejecutar

```bash
cd services/api
python3 -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
