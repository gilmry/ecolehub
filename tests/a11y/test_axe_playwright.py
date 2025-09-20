"""
Playwright + axe-core accessibility smoke test (Python).

Runs axe against the main app container and fails on 'serious' or 'critical' violations.

Usage (local):
  - Serve frontend: `make a11y-serve-frontend` (default http://localhost:8089)
  - In another terminal: `BASE_URL=http://localhost:8089 pytest -q tests/a11y/test_axe_playwright.py -m a11y`

In CI, a dedicated job serves the frontend and runs this test.
"""

import os
import pytest
from playwright.sync_api import sync_playwright


pytestmark = pytest.mark.a11y


def run_axe(page, include_selector="#app"):
    # Inject axe-core from CDN
    page.add_script_tag(
        url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js"
    )
    # Run axe with WCAG 2.1 AA
    result = page.evaluate(
        "async (sel) => {\n"
        "  const context = sel ? { include: [[sel]] } : undefined;\n"
        "  return await axe.run(context, {\n"
        "    runOnly: { type: 'tag', values: ['wcag2a','wcag2aa'] },\n"
        "    resultTypes: ['violations']\n"
        "  });\n"
        "}",
        include_selector,
    )
    return result


def format_violation(v):
    nodes = v.get("nodes", [])
    snippets = []
    for n in nodes[:5]:
        target = ", ".join(n.get("target", []))
        html = (n.get("html", "") or "").strip().replace("\n", " ")
        snippets.append(f"- target: {target}\n  html: {html}")
    return (
        f"id: {v.get('id')} | impact: {v.get('impact')} | help: {v.get('help')}\n"
        f"helpUrl: {v.get('helpUrl')}\n" + "\n".join(snippets)
    )


def test_accessibility_serious_and_critical_only():
    base_url = os.environ.get("BASE_URL", "http://localhost:8089")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(base_url, wait_until="domcontentloaded")

        axe = run_axe(page)
        violations = axe.get("violations", [])

        # Filter to serious/critical only to reduce noise in early stages
        problematic = [v for v in violations if v.get("impact") in {"serious", "critical"}]

        if problematic:
            details = "\n\n".join(format_violation(v) for v in problematic)
            pytest.fail(f"Accessibility violations detected (serious/critical):\n{details}")

        context.close()
        browser.close()

