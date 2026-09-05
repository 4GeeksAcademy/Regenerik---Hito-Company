#!/usr/bin/env python3
"""Take screenshots of the Brasaland application for PR."""

from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = Path(__file__).resolve().parent.parent / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = "http://127.0.0.1:8000"
BACKOFFICE_URL = "http://127.0.0.1:8080/uis/backoffice/index.html"
WEB_URL = "http://127.0.0.1:8080/uis/web/index.html"

TEST_EMAIL = "admin@brasaland.co"
TEST_PASSWORD = "testpass123"


def login(page, url: str) -> None:
    page.goto(url)
    page.wait_for_load_state("networkidle")

    # Fill in login form
    page.fill('input[name="email"]', TEST_EMAIL)
    page.fill('input[name="password"]', TEST_PASSWORD)
    page.click('button:has-text("Iniciar sesión")')
    page.wait_for_timeout(2000)


def take_screenshots() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="es-ES",
        )
        page = context.new_page()

        # --- Screenshot 1: Validation error on supplier form ---
        print("Taking screenshot 1: Form validation error...")
        login(page, BACKOFFICE_URL)

        # Navigate to suppliers section
        page.click('a[href="#suppliers"]')
        page.wait_for_timeout(1000)

        # Submit the supplier form with invalid data to trigger validation error
        # Try submitting with empty required fields
        page.fill('form#supplierForm input[name="name"]', "")
        page.click('form#supplierForm button:has-text("Crear proveedor")')
        page.wait_for_timeout(500)

        page.screenshot(path=str(EVIDENCE_DIR / "01-form-validation-error.png"), full_page=True)
        print(f"  Saved: {EVIDENCE_DIR / '01-form-validation-error.png'}")

        # --- Screenshot 2: Suppliers listing with data loaded ---
        print("Taking screenshot 2: Suppliers listing...")
        # Refresh suppliers
        page.fill('form#supplierForm input[name="name"]', "Test Supplier")
        page.fill('form#supplierForm input[name="categories"]', "carne")
        page.fill('form#supplierForm input[name="rate_per_unit"]', "10000")
        page.click('#refreshSuppliersBtn')
        page.wait_for_timeout(1500)

        page.screenshot(path=str(EVIDENCE_DIR / "02-suppliers-listing.png"), full_page=True)
        print(f"  Saved: {EVIDENCE_DIR / '02-suppliers-listing.png'}")

        # --- Screenshot 3: Incidents analysis results ---
        print("Taking screenshot 3: Incidents analysis results...")

        # Upload CSV and analyze
        csv_path = Path(__file__).resolve().parent.parent / "incidents-brasaland.csv"
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(str(csv_path))
        page.wait_for_timeout(500)

        page.click('#analyzeBtn')
        page.wait_for_timeout(2000)

        page.screenshot(path=str(EVIDENCE_DIR / "03-incidents-summary.png"), full_page=True)
        print(f"  Saved: {EVIDENCE_DIR / '03-incidents-summary.png'}")

        browser.close()
    print("\nAll screenshots captured successfully!")


if __name__ == "__main__":
    take_screenshots()