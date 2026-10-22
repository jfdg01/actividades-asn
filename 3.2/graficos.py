#!/usr/bin/env python3
"""Genera los gráficos SVG del informe 3.2 en img/. Uso: python3 graficos.py (solo stdlib).

Sigue la guía de gráficos de md-to-pdf (docs/charts.md); su copia de referencia es docs/charts/example.py. Los datos son los medidos con
`ab` y `docker stats`; las series de memoria salen de `docker stats` (1 muestra/s aprox.).
"""
from pathlib import Path

# --- Tokens (paleta de referencia de dataviz, modo claro) -------------------
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # categóricos 1-3, en este orden
FONT = "Space Grotesk, sans-serif"
T = 1.2  # factor de texto: las figuras se escalan a ~84 % en la página, así el texto queda en ≥ 8 pt
OUT = Path(__file__).parent / "img"


def num(v, dec=0):
    """Formato español: coma decimal, espacio duro como separador de miles."""
    s = f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


def text(x, y, s, size=11, fill=INK2, weight=400, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size * T:.1f}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>')


def hbar(x0, y, length, h, color, r=4):
    """Barra horizontal: base cuadrada en x0, extremo de datos redondeado r px."""
    if length < 0.5:
        return ""
    r = min(r, length, h / 2)
    x1 = x0 + length
    return (f'<path d="M{x0:.1f},{y:.1f} H{x1 - r:.1f} A{r},{r} 0 0 1 {x1:.1f},{y + r:.1f} '
            f'V{y + h - r:.1f} A{r},{r} 0 0 1 {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z" fill="{color}"/>')


def dot(x, y, r=4):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{INK}" '
            f'stroke="{SURFACE}" stroke-width="2"/>')


def legend(items, x, y):
    """items: (color, etiqueta, forma). Marca de color junto al texto; el texto va en tinta."""
    out, cx = [], x
    for color, label, shape in items:
        if shape == "dot":
            out.append(dot(cx + 5, y - 4))
        elif shape == "line":
            out.append(f'<rect x="{cx}" y="{y - 10}" width="2" height="12" fill="{color}"/>')
        else:
            out.append(f'<rect x="{cx}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        out.append(text(cx + 16, y, label, 11))
        cx += 16 + len(label) * 6.3 * T + 18
    return out


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            + "".join(body) + "</svg>")


def axis_ticks(x0, width, top, bottom, vmax, ticks, fmt):
    out = []
    for t in ticks:
        x = x0 + width * t / vmax
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{GRID}" stroke-width="1"/>')
        out.append(text(x, bottom + 14, fmt(t), 10, INK2, anchor="middle"))
    out.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{bottom}" stroke="{AXIS}" stroke-width="1"/>')
    return out


# --- Figura 1: memoria del frontal durante ab -c 40 (Paso 2) ----------------
MEM_150 = [14.0, 20.06, 21.43, 25.07, 32.41, 46.73, 47.08]
MEM_30 = [12.39, 16.71, 19.21, 21.54, 24.78, 32.07, 40.14, 41.08, 40.52, 41.55, 40.63, 40.61,
          41.28, 41.29, 41.24, 41.62, 41.13, 40.75, 41.35, 41.69, 41.84]


def fig_memoria():
    W, H, x0, x1, top, bot = 780, 270, 52, 570, 40, 220
    vmax, tmax = 50, 20
    X = lambda t: x0 + (x1 - x0) * t / tmax
    Y = lambda v: bot - (bot - top) * v / vmax
    b = legend([(ORANGE, "MaxRequestWorkers 150", "square"), (BLUE, "MaxRequestWorkers 30", "square")], x0, 16)
    for v in range(0, 51, 10):
        b.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        b.append(text(x0 - 8, Y(v) + 4, str(v), 10, INK2, anchor="end"))
    for t in range(0, 21, 5):
        b.append(text(X(t), bot + 16, str(t), 10, INK2, anchor="middle"))
    b.append(f'<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" stroke="{AXIS}"/>')
    b.append(text((x0 + x1) / 2, bot + 34, "segundos desde el inicio de la carga (≈ 1 muestra por segundo)", 10.5, INK2, anchor="middle"))
    b.append(text(x0 - 8, top - 10, "MiB", 10, INK2, anchor="end"))
    # límite de memoria: línea de referencia en tinta, etiquetada
    b.append(f'<line x1="{x0}" y1="{Y(48):.1f}" x2="{x1}" y2="{Y(48):.1f}" stroke="{INK2}" stroke-width="1.5"/>')
    b.append(text(x1 + 8, Y(48) + 4, "límite 48 MiB", 11, INK2))
    for series, color in ((MEM_150, ORANGE), (MEM_30, BLUE)):
        pts = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in enumerate(series))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        b.append(f'<circle cx="{X(len(series) - 1):.1f}" cy="{Y(series[-1]):.1f}" r="4" fill="{color}" '
                 f'stroke="{SURFACE}" stroke-width="2"/>')
    # etiquetas directas al final de cada serie; el texto va en tinta
    b.append(text(x1 + 8, Y(MEM_30[-1]) + 14, "41,8 MiB · 31 procesos", 11))
    b.append(text(x1 + 8, Y(MEM_30[-1]) + 28, "sin caída", 11))
    xe, ye = X(len(MEM_150) - 1), Y(MEM_150[-1])
    xl, yl = X(7.2), Y(33)  # libre bajo la línea azul; la marca naranja lo une a su serie
    b.append(f'<rect x="{xl - 16:.1f}" y="{yl - 9:.1f}" width="10" height="10" rx="2" fill="{ORANGE}"/>')
    b.append(text(xl, yl, "47,1 MiB · 42 procesos", 11))
    b.append(text(xl, yl + 14, "Parado por memoria · 3 020 peticiones", 11))
    return svg(W, H, b)


# --- Figura 2: ab, balanceador frente a un solo frontal (Paso 3) ------------
# Cada valor es [ejecución A, ejecución B]. Orden: (conexiones, destino).
RUNS = {
    ("10", "Balanceador"): {"rps": [981.44, 613.36], "media": [10, 16], "max": [941, 200]},
    ("10", "Un frontal"): {"rps": [302.49, 422.25], "media": [33, 24], "max": [295, 299]},
    ("20", "Balanceador"): {"rps": [603.77, 677.06], "media": [33, 29], "max": [4145, 2640]},
    ("20", "Un frontal"): {"rps": [492.83, 369.75], "media": [40, 54], "max": [200, 599]},
}
PANELS = [("rps", "Peticiones por segundo", "más es mejor", 1000, [0, 500, 1000]),
          ("media", "Tiempo total medio (ms)", "menos es mejor", 60, [0, 30, 60]),
          ("max", "Tiempo máximo (ms)", "menos es mejor", 4500, [0, 2000, 4000])]


def fig_ab():
    W, H, lab, pw, bh = 720, 300, 128, 128, 20
    b = legend([(BLUE, "Balanceador", "square"), (ORANGE, "Un frontal", "square"),
                (INK, "cada ejecución (barra = media de las dos)", "dot")], lab, 16)
    top = 78
    for pi, (key, title, hint, vmax, ticks) in enumerate(PANELS):
        x0 = 150 + pi * 190
        b.append(text(x0, 44, title, 12, INK, 600))
        b.append(text(x0, 58, hint, 10, INK2))
        b += axis_ticks(x0, pw, top, top + 2 * 100 - 16, vmax, ticks, lambda t: num(t))
        for gi, conns in enumerate(("10", "20")):
            gy = top + gi * 100
            if pi == 0:
                b.append(text(20, gy + 6, f"{conns} conexiones", 11.5, INK, 600))
            for ri, dest in enumerate(("Balanceador", "Un frontal")):
                y = gy + 16 + ri * 34
                runs = RUNS[(conns, dest)][key]
                mean = sum(runs) / 2
                color = BLUE if dest == "Balanceador" else ORANGE
                if pi == 0:
                    b.append(text(lab - 10, y + 15, dest, 11, INK2, anchor="end"))
                b.append(hbar(x0, y, pw * mean / vmax, bh, color))
                for r in runs:
                    b.append(dot(x0 + pw * r / vmax, y + bh / 2))
                tip = x0 + pw * max(mean, *runs) / vmax + 10
                b.append(text(tip, y + 15, num(mean, 0), 11, INK, 600))
    return svg(W, H, b)


# --- Figura 3: picos de CPU y memoria por contenedor (Paso 3) ---------------
ESCENARIOS = ["Balanceador, 10 conexiones", "Un frontal, 10 conexiones",
              "Balanceador, 20 conexiones", "Un frontal, 20 conexiones"]
CPU = [(26.3, 24.8, 46.1), (25.9, 0.0, 0.5), (26.3, 24.3, 37.4), (27.0, 0.5, 0.3)]
MEM = [(35.2, 28.0, 39.5), (33.6, 23.0, 35.9), (43.6, 33.1, 43.6), (43.3, 26.4, 40.8)]


def fig_recursos():
    W, H, lab, pw, bh, gap = 720, 400, 170, 130, 12, 2
    colors = [BLUE, ORANGE, AQUA]
    b = legend([(BLUE, "Frontal 1", "square"), (ORANGE, "Frontal 2", "square"),
                (AQUA, "traefik (sin límite de recursos)", "square")], lab, 16)
    top, group = 78, 74
    bottom = top + 4 * group - 14
    for pi, (title, data, vmax, ticks, limit, limit_txt, dec) in enumerate([
            ("CPU máxima (% de un núcleo)", CPU, 60, [0, 20, 40, 60], 25, "límite 25 %", 1),
            ("Memoria máxima (MiB)", MEM, 60, [0, 20, 40, 60], 48, "límite 48 MiB", 1)]):
        x0 = lab + pi * 270
        b.append(text(x0, 46, title, 12, INK, 600))
        b += axis_ticks(x0, pw, top, bottom, vmax, ticks, lambda t: num(t))
        lx = x0 + pw * limit / vmax
        b.append(f'<line x1="{lx:.1f}" y1="{top - 6}" x2="{lx:.1f}" y2="{bottom}" stroke="{INK2}" stroke-width="1.5"/>')
        b.append(text(lx, top - 12, limit_txt, 10, INK2, anchor="middle"))
        for si, vals in enumerate(data):
            gy = top + si * group
            if pi == 0:
                b.append(text(lab - 12, gy + 24, ESCENARIOS[si].split(",")[0], 11.5, INK, 600, "end"))
                b.append(text(lab - 12, gy + 38, ESCENARIOS[si].split(", ")[1], 10.5, INK2, anchor="end"))
            for k, v in enumerate(vals):
                y = gy + 4 + k * (bh + gap)
                b.append(hbar(x0, y, pw * v / vmax, bh, colors[k], r=3))
                lw = len(num(v, dec)) * 5.8 * T + 4
                b.append(f'<rect x="{x0 + pw * v / vmax + 5:.1f}" y="{y}" width="{lw:.1f}" height="{bh}" fill="{SURFACE}"/>')
                b.append(text(x0 + pw * v / vmax + 7, y + 10, num(v, dec), 10, INK))
    return svg(W, H, b)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in (("memoria-apache", fig_memoria), ("ab-resultados", fig_ab), ("recursos-picos", fig_recursos)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("escrito", OUT / f"{name}.svg")
