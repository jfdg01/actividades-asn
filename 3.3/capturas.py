"""Captura el panel de Traefik del servicio wwwserver@docker en un PNG.

Uso: uv run --with playwright python -I capturas.py img/<nombre>.png [services|routers]

La captura va del título hasta la última tarjeta antes de "Used by routers"
(página del servicio) o de "TLS" (página del router), sin margen propio, como
pide md-to-pdf.
"""
import sys

from playwright.sync_api import sync_playwright

PAGINA = sys.argv[2] if len(sys.argv) > 2 else "services"
URL = f"http://localhost:8080/dashboard/#/http/{PAGINA}/wwwserver@docker"

# Rectángulo de las tarjetas del servicio en la columna principal del panel.
RECORTE = """() => {
  const col = [...document.querySelectorAll('h1, section, div')].filter(e => {
    const r = e.getBoundingClientRect();
    return r.left === 288 && r.width === 968;
  });
  const titulo = col.find(e => e.tagName === 'H1').getBoundingClientRect();
  const rutas = col.find(e => /^(Used by routers|TLS)/.test(e.innerText)).getBoundingClientRect();
  const fondo = Math.max(...col.map(e => e.getBoundingClientRect().bottom)
                              .filter(b => b <= rutas.top));
  return {x: titulo.left, y: titulo.top, width: titulo.width, height: fondo - titulo.top};
}"""

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page(viewport={"width": 1280, "height": 1000}, device_scale_factor=2)
    pagina.goto(URL)
    pagina.wait_for_selector("text=Servers" if PAGINA == "services" else "text=HTTP Middlewares")
    pagina.wait_for_timeout(1000)
    pagina.screenshot(path=sys.argv[1], clip=pagina.evaluate(RECORTE))
    navegador.close()
