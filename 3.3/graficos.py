#!/usr/bin/env python3
"""Genera los gráficos SVG del informe 3.3 en img/. Uso: python3 -I graficos.py (solo stdlib).

Sigue la guía de gráficos de md-to-pdf (~/md-to-pdf/docs/charts.md), con las funciones de 3.2/graficos.py.
Los datos salen de las pruebas de notas/: el log de acceso de traefik, la salida de ab y docker stats.
"""
from pathlib import Path

SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE = "#2a78d6", "#eb6834"
FONT = "Space Grotesk, sans-serif"
T = 1.2  # factor de texto: las figuras se escalan a ~84 % en la página, así el texto queda en ≥ 8 pt
OUT = Path(__file__).parent / "img"


def text(x, y, s, size=11, fill=INK2, weight=400, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size * T:.1f}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')


def num(v, dec=0):
    """Formato español: coma decimal, espacio como separador de miles."""
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def hbar(x0, y, length, h, color, r=4):
    """Barra horizontal: base cuadrada en x0, extremo de datos redondeado r px."""
    if length < 0.5:
        length = 0.5
    r = min(r, length, h / 2)
    x1 = x0 + length
    return (f'<path d="M{x0:.1f},{y:.1f} H{x1 - r:.1f} A{r},{r} 0 0 1 {x1:.1f},{y + r:.1f} '
            f'V{y + h - r:.1f} A{r},{r} 0 0 1 {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z" fill="{color}"/>')


def axis_ticks(x0, width, top, bottom, vmax, ticks, fmt):
    out = []
    for t in ticks:
        x = x0 + width * t / vmax
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{GRID}" stroke-width="1"/>')
        out.append(text(x, bottom + 14, fmt(t), 10, INK2, anchor="middle"))
    out.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{bottom}" stroke="{AXIS}" stroke-width="1"/>')
    return out


def legend(items, x, y):
    """items: (color, etiqueta). Marca de color junto al texto; el texto va en tinta."""
    out, cx = [], x
    for color, label in items:
        out.append(f'<rect x="{cx}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        out.append(text(cx + 16, y, label, 11))
        cx += 16 + len(label) * 6.3 * T + 18
    return out


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + "".join(body) + "</svg>")


# --- Respuestas aceptadas por segundo con solo rateLimit ---------------------
# Respuestas 200 en cada segundo del log, desde el primer segundo de la prueba.
UNA_CONEXION = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 50]  # ab -c 1 -t 10
CINCUENTA = [52, 2, 5, 4, 0, 0, 0, 0, 0]                                # ab -c 50 -n 100000


def fig_ratelimit():
    W, H, x0, x1, top, bot = 780, 290, 52, 570, 60, 240
    vmax, tmax = 125, 11
    X = lambda t: x0 + (x1 - x0) * (t - 1) / (tmax - 1)
    Y = lambda v: bot - (bot - top) * v / vmax
    b = legend([(BLUE, "1 conexión"), (ORANGE, "50 conexiones")], x0, 16)
    for v in range(0, 126, 25):
        b.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        b.append(text(x0 - 8, Y(v) + 4, str(v), 10, INK2, anchor="end"))
    for t in range(1, tmax + 1):
        b.append(text(X(t), bot + 16, str(t), 10, INK2, anchor="middle"))
    b.append(f'<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" stroke="{AXIS}"/>')
    b.append(text((x0 + x1) / 2, bot + 34, "segundo de la prueba", 10.5, INK2, anchor="middle"))
    b.append(text(x0 - 8, top - 16, "respuestas 200 por segundo", 10, INK2))
    # límite configurado: línea de referencia en tinta, etiquetada
    b.append(f'<line x1="{x0}" y1="{Y(100):.1f}" x2="{x1}" y2="{Y(100):.1f}" stroke="{INK2}" stroke-width="1.5"/>')
    b.append(text(x1 + 8, Y(100) + 4, "average: 100 por segundo", 11, INK2))
    for series, color in ((UNA_CONEXION, BLUE), (CINCUENTA, ORANGE)):
        pts = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in enumerate(series, 1))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        b.append(f'<circle cx="{X(len(series)):.1f}" cy="{Y(series[-1]):.1f}" r="4" fill="{color}" '
                 f'stroke="{SURFACE}" stroke-width="2"/>')
    # etiquetas: la azul al final de su serie; la naranja en el hueco libre, con su marca de color
    xa, ya = x1 + 12, Y(UNA_CONEXION[-1])
    b.append(text(xa, ya - 10, "1 conexión", 11, INK, 600))
    b.append(text(xa, ya + 6, "1 050 aceptadas", 11))
    b.append(text(xa, ya + 20, "12 899 rechazadas", 11))
    xn, yn = X(5.6), Y(55)
    b.append(f'<rect x="{xn - 16:.1f}" y="{yn - 9:.1f}" width="10" height="10" rx="2" fill="{ORANGE}"/>')
    b.append(text(xn, yn, "50 conexiones", 11, INK, 600))
    b.append(text(xn, yn + 16, "63 aceptadas", 11))
    b.append(text(xn, yn + 30, "99 937 rechazadas", 11))
    return svg(W, H, b)


# --- Prueba conjunta: un atacante y un usuario, sin y con protección (infográfico) ---
# Atacante: ab -c 50 -t 20 desde la red de Compose (notas/30-* y 31-*). Usuario: 50 curl, uno cada 0,3 s.
CONJUNTA = {
    "sin": {"enviadas": 17785, "servidas": 17785, "peor": 3068.6, "media": 66.8, "cpu": 27, "mem": 46.7},
    "con": {"enviadas": 268374, "servidas": 23, "peor": 2.6, "media": 1.6, "cpu": 1, "mem": 25.4},
}
AQUA = "#1baf7a"


def persona(cx, cy, color, s=1.0):
    """Icono de persona: cabeza y hombros."""
    return (f'<circle cx="{cx:.1f}" cy="{cy - 8 * s:.1f}" r="{6.5 * s:.1f}" fill="{color}"/>'
            f'<path d="M{cx - 11 * s:.1f},{cy + 13 * s:.1f} a{11 * s:.1f},{11 * s:.1f} 0 0 1 {22 * s:.1f},0 Z" fill="{color}"/>')


def servidor(x, y, color):
    """Icono de servidor: una caja con dos ranuras."""
    return (f'<rect x="{x}" y="{y}" width="28" height="22" rx="4" fill="{color}"/>'
            f'<line x1="{x + 6}" y1="{y + 8}" x2="{x + 22}" y2="{y + 8}" stroke="{SURFACE}" stroke-width="2" stroke-linecap="round"/>'
            f'<line x1="{x + 6}" y1="{y + 15}" x2="{x + 22}" y2="{y + 15}" stroke="{SURFACE}" stroke-width="2" stroke-linecap="round"/>')


def flecha(x1, y1, x2, y2, color, w):
    """Flecha recta con punta triangular en (x2, y2)."""
    p = 4 + w * 1.5
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2 - p}" y2="{y2}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{x2 - p - 1},{y2 - p * 0.7:.1f} L{x2},{y2} L{x2 - p - 1},{y2 + p * 0.7:.1f} Z" fill="{color}"/>')


def medidor(x, y, w, fraccion, color):
    """Barra de progreso: pista gris y relleno de color, extremos redondeados."""
    f = max(0.0, min(fraccion, 1.0))
    out = f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="{GRID}"/>'
    return out + f'<rect x="{x}" y="{y}" width="{max(w * f, 8):.1f}" height="8" rx="4" fill="{color}"/>'


def cifra(x, y, grande, nota):
    """Una cifra grande y su nota en la misma línea: el tspan pone la nota justo detrás."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" fill="{INK}">'
            f'<tspan font-size="{24 * T:.1f}" font-weight="700">{grande}</tspan>'
            f'<tspan dx="8" font-size="{11 * T:.1f}" fill="{INK2}">{nota}</tspan></text>')


def tarjeta(x, y, w, h, titulo, lema, d):
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{SURFACE}" stroke="{GRID}" stroke-width="1.5"/>',
         text(x + 22, y + 32, titulo, 14, INK, 700), text(x + 22, y + 50, lema, 10.5, INK2)]
    ix, tx = x + 34, x + 62
    # el atacante: peticiones servidas de las enviadas
    ry = y + 80
    b += [persona(ix, ry + 16, ORANGE), text(tx, ry, "ATACANTE", 9.5, INK2, 600),
          cifra(tx, ry + 30, num(d["servidas"]), f"servidas de {num(d['enviadas'])}"),
          medidor(tx, ry + 42, w - 90, d["servidas"] / d["enviadas"], ORANGE)]
    # el usuario: la peor espera
    ry = y + 160
    peor = f"{num(d['peor'] / 1000, 1)} s" if d["peor"] >= 1000 else f"{num(d['peor'], 1)} ms"
    b += [persona(ix, ry + 16, BLUE), text(tx, ry, "USUARIO", 9.5, INK2, 600),
          cifra(tx, ry + 30, peor, "la peor espera"),
          text(tx, ry + 50, f"media {num(d['media'], 1)} ms · 50 de 50 con 200", 10.5, INK2)]
    # cada frontal: CPU y memoria frente a su límite
    ry = y + 240
    b += [servidor(ix - 14, ry + 6, AQUA), text(tx, ry, "CADA FRONTAL", 9.5, INK2, 600)]
    mw = (w - 90 - 24) / 2
    for k, (valor, sufijo, limite, nota) in enumerate(((d["cpu"], " %", 25, "CPU · límite 25 %"),
                                                        (d["mem"], " MiB", 48, "memoria · límite 48 MiB"))):
        mx = tx + k * (mw + 24)
        b += [text(mx, ry + 26, num(valor, 0 if sufijo == " %" else 1) + sufijo, 16, INK, 700),
              medidor(mx, ry + 34, mw, valor / limite, AQUA), text(mx, ry + 58, nota, 10, INK2)]
    return b


def fig_prueba_conjunta():
    W, H = 780, 492
    b = []
    # el escenario: dos clientes con IP distintas, traefik con su cadena y los dos frontales
    b += [persona(30, 46, ORANGE), text(52, 42, "Atacante", 12, INK, 700), text(52, 58, "172.19.0.6 · 50 conexiones", 10, INK2),
          persona(30, 116, BLUE), text(52, 112, "Usuario", 12, INK, 700), text(52, 128, "172.19.0.1 · 1 cada 0,3 s", 10, INK2)]
    b += [flecha(232, 50, 298, 72, ORANGE, 7), flecha(232, 116, 298, 94, BLUE, 2.5)]
    b += [f'<rect x="304" y="22" width="230" height="122" rx="12" fill="{SURFACE}" stroke="{AXIS}" stroke-width="1.5"/>',
          text(320, 46, "traefik", 12, INK, 700)]
    for k, (nombre, detalle) in enumerate((("rateLimit", "100/s por IP"), ("inFlightReq", "20 en curso"))):
        cx = 320 + k * 110
        b += [f'<rect x="{cx}" y="62" width="92" height="30" rx="15" fill="{GRID}"/>',
              text(cx + 46, 82, nombre, 10.5, INK, 600, "middle"), text(cx + 46, 110, detalle, 9.5, INK2, anchor="middle")]
    b += [flecha(414, 77, 428, 77, INK2, 1.5), flecha(540, 83, 596, 83, INK2, 2.5)]
    for k, nombre in enumerate(("wwwserver-1", "wwwserver-2")):
        y = 40 + k * 60
        b += [servidor(604, y, AQUA), text(642, y + 12, nombre, 11, INK, 600), text(642, y + 27, "0,25 CPU · 48 MiB", 9.5, INK2)]
    # las dos tarjetas: la misma prueba sin y con los middlewares
    b += tarjeta(0, 172, 382, 312, "Sin protección", "el atacante llena las colas de los frontales", CONJUNTA["sin"])
    b += tarjeta(398, 172, 382, 312, "Con rateLimit e inFlightReq", "cada IP tiene su propio cubo de tokens", CONJUNTA["con"])
    return svg(W, H, b)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for nombre, fn in (("ratelimit-por-segundo", fig_ratelimit), ("prueba-conjunta", fig_prueba_conjunta)):
        (OUT / f"{nombre}.svg").write_text(fn(), encoding="utf-8")
        print(f"img/{nombre}.svg")
