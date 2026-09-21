from __future__ import annotations

from pathlib import Path

from database import SUPPLIERS_SEED, SupplierStore


def main() -> None:
    storage_path = Path(__file__).resolve().parent / "data" / "suppliers.json"
    store = SupplierStore(storage_path=storage_path)

    inserted, skipped = store.seed_suppliers(SUPPLIERS_SEED)
    total = len(store.list())

    print(f"Seed completado. Insertados: {inserted}. Omitidos: {skipped}. Total actual: {total}.")


if __name__ == "__main__":
    main()
