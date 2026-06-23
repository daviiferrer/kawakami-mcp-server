import re
from pathlib import Path

from src.config import settings

WIDGET_URI = "ui://kawakami/catalog-v1.html"
WIDGET_MIME_TYPE = "text/html;profile=mcp-app"
WIDGET_DIST_DIR = Path(__file__).resolve().parents[2] / "ui" / "dist"
IMAGE_DOMAIN = "https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com"

WIDGET_TOOL_META = {
    "ui": {"resourceUri": WIDGET_URI},
    "openai/outputTemplate": WIDGET_URI,
}

WIDGET_RESOURCE_META = {
    "ui": {
        "prefersBorder": True,
        "domain": settings.widget_domain,
        "csp": {
            "connectDomains": [],
            "resourceDomains": [IMAGE_DOMAIN],
            "frameDomains": [],
        },
    },
    "openai/widgetDescription": "Exibe produtos e ofertas do Supermercados Kawakami.",
}


def load_widget_html(dist_dir: Path = WIDGET_DIST_DIR) -> str:
    """Carrega o build Vite e embute CSS/JavaScript no resource MCP."""
    index_path = dist_dir / "index.html"
    if not index_path.exists():
        return (
            '<!doctype html><html><body><div id="root">'
            "Widget indisponivel: execute o build da UI."
            "</div></body></html>"
        )

    html = index_path.read_text(encoding="utf-8")

    def inline_stylesheet(match: re.Match[str]) -> str:
        asset_path = dist_dir / match.group("path").lstrip("/")
        return f"<style>{asset_path.read_text(encoding='utf-8')}</style>"

    def inline_script(match: re.Match[str]) -> str:
        asset_path = dist_dir / match.group("path").lstrip("/")
        return f'<script type="module">{asset_path.read_text(encoding="utf-8")}</script>'

    html = re.sub(
        r'<link[^>]+rel="stylesheet"[^>]+href="(?P<path>[^"]+)"[^>]*>',
        inline_stylesheet,
        html,
    )
    return re.sub(
        r'<script[^>]+type="module"[^>]+src="(?P<path>[^"]+)"[^>]*></script>',
        inline_script,
        html,
    )
