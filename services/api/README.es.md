# API de Incidencias Brasaland

Servicio backend para analisis de incidencias y gestion del directorio de proveedores.

Stack del directorio de proveedores: FastAPI + TinyDB + Pydantic.

## Endpoints

### Directorio de proveedores (almacenamiento ligero)

- `GET /suppliers`
  - Filtros opcionales por query: `country`, `category`, `status`.
  - Devuelve `{ "items": [...], "total": number }`.

- `GET /suppliers/{supplier_id}`
  - Devuelve el detalle de un proveedor por ID.
  - Responde `404` si no existe.

- `POST /suppliers`
  - Crea un proveedor.
  - Errores de payload invalidos se devuelven con `422` (validacion de FastAPI/Pydantic).
  - Valida reglas de negocio del contexto:
    - `country` debe ser `Colombia` o `USA`.
    - `currency` debe coincidir con el pais (`COP` para Colombia, `USD` para USA).
    - `categories` debe contener una o mas categorias validas.

- `PATCH /suppliers/{supplier_id}/rate`
  - Actualiza `rate_per_unit` y refresca el timestamp `updated_at`.

- `PATCH /suppliers/{supplier_id}/status`
  - Cambia `status` a `active` o `suspended`.

- `DELETE /suppliers/{supplier_id}`
  - Elimina un proveedor (pensado para correcciones de datos).

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

Los datos de proveedores se persisten en TinyDB en `services/api/data/suppliers.json`.
En el primer arranque, el archivo se auto-puebla con el seeder de Brasaland.

## Seeder

- Script: `services/api/seed.py`
- Ejecucion: `uv run seed` (desde `services/api`)
- Comportamiento: inserta solo proveedores no existentes (evita duplicados) y reporta en consola inserciones/omitidos.
