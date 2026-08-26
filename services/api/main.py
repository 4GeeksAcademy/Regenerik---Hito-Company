from __future__ import annotations

import sys
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.incidents_analysis import (  # noqa: E402
    analyze_csv_text,
    metrics_rows_to_csv,
    to_metrics_rows,
    to_summary,
)
from auth import get_current_user  # noqa: E402
from routes.auth import router as auth_router  # noqa: E402
from routes.profiles import router as profiles_router  # noqa: E402
from routes.suppliers import router as suppliers_router  # noqa: E402
from routes.users import router as users_router  # noqa: E402

app = FastAPI(title="Brasaland Operations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LATEST_SUMMARY: dict | None = None
LATEST_RESULTS_CSV: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/incidents/analyze", dependencies=[Depends(get_current_user)])
async def analyze_incidents(file: UploadFile = File(...)) -> JSONResponse:
    global LATEST_SUMMARY, LATEST_RESULTS_CSV

    if not file.filename:
        raise HTTPException(status_code=400, detail="Debes enviar un archivo CSV")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Formato incorrecto: se espera un archivo .csv")

    raw_content = await file.read()
    if not raw_content:
        raise HTTPException(status_code=400, detail="El fichero está vacío")

    try:
        csv_text = raw_content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="El archivo debe estar en UTF-8") from error

    if not csv_text.strip():
        raise HTTPException(status_code=400, detail="El fichero está vacío")

    try:
        result = analyze_csv_text(csv_text)
        summary = to_summary(result, source_file=file.filename)
        rows = to_metrics_rows(summary)
        csv_output = metrics_rows_to_csv(rows)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"No se pudo analizar el CSV: {error}") from error

    LATEST_SUMMARY = summary
    LATEST_RESULTS_CSV = csv_output

    return JSONResponse(content=summary)


@app.get("/api/incidents/results/export", dependencies=[Depends(get_current_user)])
def export_last_results() -> Response:
    if LATEST_RESULTS_CSV is None:
        raise HTTPException(status_code=404, detail="No hay resultados para exportar. Ejecuta primero el análisis.")

    return Response(
        content=LATEST_RESULTS_CSV,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=results.csv"},
    )


@app.get("/api/incidents/results/latest", dependencies=[Depends(get_current_user)])
def latest_results() -> JSONResponse:
    if LATEST_SUMMARY is None:
        raise HTTPException(status_code=404, detail="No hay análisis ejecutados todavía")
    return JSONResponse(content=LATEST_SUMMARY)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(suppliers_router, dependencies=[Depends(get_current_user)])
app.include_router(suppliers_router, prefix="/api", dependencies=[Depends(get_current_user)])
