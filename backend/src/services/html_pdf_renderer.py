"""
HTML to PDF renderer using Playwright
Renders a magazine-style HTML template with Jinja2 and converts to PDF.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

class HTMLPDFRenderer:
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_html(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_pdf(self, html_content: str, output_path: Path) -> Path:
        """Render given HTML content to PDF using Playwright. Raises if Playwright not available."""
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            raise RuntimeError("Playwright is not installed. Run: python -m playwright install chromium") from e

        output_path.parent.mkdir(parents=True, exist_ok=True)
        html_file = output_path.with_suffix('.html')
        html_file.write_text(html_content, encoding='utf-8')

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_file}")
            # Optional: wait for network idle or fonts loading
            page.wait_for_load_state("networkidle")
            page.pdf(path=str(output_path), format="A4", print_background=True, margin={"top":"20mm","bottom":"20mm","left":"15mm","right":"15mm"})
            browser.close()
        return output_path

    def render_magazine_pdf(self, guide: Dict[str, Any], itinerary: Dict[str, Any], output_path: Path) -> Path:
        html = self.render_html("magazine_guide.html", {
            "guide": guide,
            "itinerary": itinerary,
        })
        return self.render_pdf(html, output_path)

