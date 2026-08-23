"""Capture high-resolution real prototype screenshots for TEKNOFEST Report Evidence Pack."""

import os
import shutil
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "report_assets", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"


def capture_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 960},
            device_scale_factor=2,
        )
        page = context.new_page()

        # =========================================================================
        # 1. Main Feed
        # =========================================================================
        print("1. Capturing 01: Main Feed...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        time.sleep(3)
        path_01 = os.path.join(OUTPUT_DIR, "screenshot_01_main_feed.png")
        page.screenshot(path=path_01)
        print(f"Saved: {path_01}")

        # =========================================================================
        # 2. Semantic Search
        # =========================================================================
        print("2. Capturing 02: Semantic Search...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        time.sleep(2)
        search_input = page.locator("input[type='text']").first
        search_input.fill("yapay zeka ve eğitim alanındaki gelişmeler")
        page.get_by_role("button", name="Ara", exact=True).click()
        time.sleep(3.5)
        path_02 = os.path.join(OUTPUT_DIR, "screenshot_02_semantic_search.png")
        page.screenshot(path=path_02)
        print(f"Saved: {path_02}")

        # =========================================================================
        # 3. Explainable Recommendation Modal
        # =========================================================================
        print("3. Capturing 03: Explainable Recommendation...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        time.sleep(3)
        # Find the first explain button using text regex
        explain_btns = page.locator("button:has-text('Neden Görüyorum?')").all()
        print(f"Found {len(explain_btns)} explain buttons")
        if explain_btns:
            explain_btns[0].scroll_into_view_if_needed()
            time.sleep(1)
            explain_btns[0].click()
            time.sleep(2.5)
            path_03 = os.path.join(OUTPUT_DIR, "screenshot_03_explainability.png")
            page.screenshot(path=path_03)
            print(f"Saved: {path_03}")
            shutil.copy(path_03, os.path.join(OUTPUT_DIR, "screenshot_03_explainable_recommendation.png"))

        # =========================================================================
        # 4. Context Card Modal (Real Semantic Cluster)
        # =========================================================================
        print("4. Capturing 04: Context Card (Bağlam Kartı)...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        time.sleep(3)
        context_btns = page.locator("button:has-text('Bağlamı Gör')").all()
        print(f"Found {len(context_btns)} context buttons")
        if context_btns:
            context_btns[0].scroll_into_view_if_needed()
            time.sleep(1)
            context_btns[0].click()
            time.sleep(3.5)
            path_04 = os.path.join(OUTPUT_DIR, "screenshot_04_contextual_dashboard.png")
            page.screenshot(path=path_04)
            print(f"Saved: {path_04}")
            shutil.copy(path_04, os.path.join(OUTPUT_DIR, "screenshot_04_context_card.png"))

        # =========================================================================
        # 5. Content Safety & Moderation Lab
        # =========================================================================
        print("5. Capturing 05: Content Safety & Moderation Lab...")
        page.goto("http://localhost:3000/", wait_until="networkidle")
        time.sleep(3)
        safety_btn = page.locator("button:has-text('Güvenlik Lab')").first
        safety_btn.click()
        time.sleep(2)
        # Click the test sample button
        sample_pill = page.locator("button:has-text('Hakaret'), button:has-text('Spam'), button:has-text('Tehdit')").first
        if sample_pill.is_visible():
            sample_pill.click()
            time.sleep(1)
        analyze_btn = page.locator("button:has-text('İçeriği Denetle'), button:has-text('Analiz Et')").first
        if analyze_btn.is_visible():
            analyze_btn.click()
            time.sleep(3)
        path_05 = os.path.join(OUTPUT_DIR, "screenshot_05_security_moderation.png")
        page.screenshot(path=path_05)
        print(f"Saved: {path_05}")
        shutil.copy(path_05, os.path.join(OUTPUT_DIR, "screenshot_05_safety_moderation_lab.png"))

        browser.close()
        print("\nAll 5 prototype screenshots captured successfully!")


if __name__ == "__main__":
    capture_all()
