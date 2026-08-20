from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from tinydb import Query, TinyDB

from models import Supplier, SupplierCreate

SUPPLIERS_SEED: list[dict[str, Any]] = [
    {
        "name": "Carnes del Valle S.A.S.",
        "country": "Colombia",
        "categories": ["carne"],
        "rate_per_unit": 28500.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "ventas@carnesdelvalle.co",
        "notes": "Proveedor principal de res y cerdo para Medellín. Entrega martes y viernes.",
    },
    {
        "name": "Frigorífico Antioqueño",
        "country": "Colombia",
        "categories": ["carne"],
        "rate_per_unit": 27900.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "pedidos@frigorificoa.co",
        "notes": "Proveedor secundario. Usado cuando Carnes del Valle no tiene stock.",
    },
    {
        "name": "Verduras La Cosecha",
        "country": "Colombia",
        "categories": ["verduras_y_hortalizas"],
        "rate_per_unit": 3200.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "lacosecha@gmail.com",
        "notes": "Mercado mayorista de Medellín. Entrega diaria antes de las 7am.",
    },
    {
        "name": "Condimentos El Sabor",
        "country": "Colombia",
        "categories": ["salsas_y_condimentos"],
        "rate_per_unit": 12400.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "info@elsabor.co",
    },
    {
        "name": "Distribuidora RefriCol",
        "country": "Colombia",
        "categories": ["bebidas", "lacteos"],
        "rate_per_unit": 4100.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "refricol.pedidos@gmail.com",
    },
    {
        "name": "Empaques y Más",
        "country": "Colombia",
        "categories": ["packaging"],
        "rate_per_unit": 890.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "ventas@empaquesymas.co",
        "notes": "Suministra cajas, bolsas y servilletas para todos los locales de Colombia.",
    },
    {
        "name": "Limpiahogar Profesional",
        "country": "Colombia",
        "categories": ["productos_limpieza"],
        "rate_per_unit": 7600.0,
        "currency": "COP",
        "status": "suspended",
        "contact_email": "limpiahogar@promail.co",
        "notes": "Suspendido por incumplimiento en entregas. En revisión por Lucía.",
    },
    {
        "name": "CarboCo",
        "country": "Colombia",
        "categories": ["carbon_y_combustible"],
        "rate_per_unit": 45000.0,
        "currency": "COP",
        "status": "active",
        "contact_email": "pedidos@carboco.co",
        "notes": "Único proveedor homologado de carbón para las brasas. Contrato anual.",
    },
    {
        "name": "Miami Meat Distributors LLC",
        "country": "USA",
        "categories": ["carne"],
        "rate_per_unit": 6.80,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@miamimeat.com",
        "notes": "Proveedor principal de carne para los locales de Florida.",
    },
    {
        "name": "Sunshine Produce FL",
        "country": "USA",
        "categories": ["verduras_y_hortalizas"],
        "rate_per_unit": 2.15,
        "currency": "USD",
        "status": "active",
        "contact_email": "sales@sunshineproduce.com",
    },
    {
        "name": "Latin Flavors Inc.",
        "country": "USA",
        "categories": ["salsas_y_condimentos", "bebidas"],
        "rate_per_unit": 4.50,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@latinflavors.com",
        "notes": "Importa salsas colombianas para el mercado de Florida.",
    },
    {
        "name": "PackRight USA",
        "country": "USA",
        "categories": ["packaging"],
        "rate_per_unit": 0.35,
        "currency": "USD",
        "status": "active",
        "contact_email": "info@packright.us",
    },
    {
        "name": "CleanPro Florida",
        "country": "USA",
        "categories": ["productos_limpieza"],
        "rate_per_unit": 12.90,
        "currency": "USD",
        "status": "active",
        "contact_email": "orders@cleanproflorida.com",
    },
    {
        "name": "GrillFuel Supply Co.",
        "country": "USA",
        "categories": ["carbon_y_combustible"],
        "rate_per_unit": 38.50,
        "currency": "USD",
        "status": "active",
        "contact_email": "supply@grillfuel.com",
        "notes": "Proveedor de carbón para Florida. Precio sujeto a revisión trimestral.",
    },
    {
        "name": "Bebidas Andinas",
        "country": "Colombia",
        "categories": ["bebidas"],
        "rate_per_unit": 3800.0,
        "currency": "COP",
        "status": "suspended",
        "contact_email": "ventas@bebidasandinas.co",
        "notes": "Suspendido. Precio por encima del mercado tras última renegociación.",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupplierStore:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self._lock = Lock()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = TinyDB(self.storage_path, ensure_ascii=False, indent=2)
        self._table = self._db.table("suppliers")
        self._query = Query()
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        self.seed_suppliers(SUPPLIERS_SEED)

    def seed_suppliers(self, suppliers_seed: list[dict[str, Any]]) -> tuple[int, int]:
        inserted = 0
        skipped = 0

        with self._lock:
            for supplier in suppliers_seed:
                payload = SupplierCreate(**supplier).model_dump()
                existing = self._table.get(
                    (self._query.name == payload["name"]) & (self._query.country == payload["country"])
                )

                if existing is not None:
                    skipped += 1
                    continue

                payload["id"] = str(uuid4())
                payload["updated_at"] = now_iso()
                self._table.insert(payload)
                inserted += 1

        return inserted, skipped

    def list(
        self,
        country: str | None = None,
        category: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        records = self._table.all()
        filtered = []
        for record in records:
            if country and record["country"] != country:
                continue
            if status and record["status"] != status:
                continue
            if category and category not in record["categories"]:
                continue
            filtered.append(record)
        return filtered

    def create(self, payload: SupplierCreate) -> dict[str, Any]:
        with self._lock:
            new_record = payload.model_dump()
            new_record["id"] = str(uuid4())
            new_record["updated_at"] = now_iso()
            self._table.insert(new_record)
            return new_record

    def get(self, supplier_id: str) -> dict[str, Any] | None:
        return self._table.get(self._query.id == supplier_id)

    def update_rate(self, supplier_id: str, new_rate: float) -> dict[str, Any] | None:
        with self._lock:
            current = self.get(supplier_id)
            if current is None:
                return None

            updated = dict(current)
            updated["rate_per_unit"] = new_rate
            updated["updated_at"] = now_iso()
            Supplier(**updated)

            self._table.update(
                {"rate_per_unit": updated["rate_per_unit"], "updated_at": updated["updated_at"]},
                self._query.id == supplier_id,
            )
            return updated

    def update_status(self, supplier_id: str, new_status: str) -> dict[str, Any] | None:
        with self._lock:
            current = self.get(supplier_id)
            if current is None:
                return None

            updated = dict(current)
            updated["status"] = new_status
            Supplier(**updated)

            self._table.update({"status": updated["status"]}, self._query.id == supplier_id)
            return updated

    def delete(self, supplier_id: str) -> bool:
        with self._lock:
            removed_ids = self._table.remove(self._query.id == supplier_id)
            return bool(removed_ids)
