"""Generate topographic contour textures for the Found in Meta deck.

Fractal value noise with a domain warp is drawn as contour lines, then faded
into the slide background so the texture sits on the right and dissolves
behind the text on the left.
"""
import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

W, H = 1920, 1080
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

# slide id -> (background, line colour, peak opacity)
SLIDES = {
    "cover": ("#1A3570", "#8FAAE6", 0.55),
    "quickfix": ("#F1F3F6", "#1F45C8", 0.38),
    "query": ("#E2E7EE", "#1F45C8", 0.30),
    "checks": ("#F1F3F6", "#1F45C8", 0.30),
    "finding": ("#1A3570", "#8FAAE6", 0.45),
    "unknowns": ("#F1F3F6", "#1F45C8", 0.38),
    "outcomes": ("#E2E7EE", "#1F45C8", 0.30),
    "output": ("#F1F3F6", "#1F45C8", 0.38),
    "mapping": ("#E2E7EE", "#1F45C8", 0.30),
    "approach": ("#F1F3F6", "#1F45C8", 0.38),
    "close": ("#1A3570", "#8FAAE6", 0.55),
}


def hex_rgb(h):
    return np.array([int(h[i : i + 2], 16) for i in (1, 3, 5)], dtype=np.float64)


def smooth_grid(rng, cells_x, cells_y, w, h):
    grid = rng.random((cells_y + 1, cells_x + 1)).astype(np.float32)
    img = Image.fromarray(grid, mode="F").resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float64)


def fractal(rng, w, h, base=3, octaves=5):
    total, amp, norm = np.zeros((h, w)), 1.0, 0.0
    for o in range(octaves):
        cx = base * 2**o
        cy = max(2, round(cx * h / w))
        total += amp * smooth_grid(rng, cx, cy, w, h)
        norm += amp
        amp *= 0.5
    return total / norm


def field(seed, w=960, h=540):
    rng = np.random.default_rng(seed)
    wx = fractal(rng, w, h, base=2, octaves=3)
    wy = fractal(rng, w, h, base=2, octaves=3)
    base = fractal(rng, w, h, base=3, octaves=5)
    # domain warp: sample the base field at displaced coordinates
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float64)
    coords = [ys + (wy - 0.5) * h * 0.35, xs + (wx - 0.5) * w * 0.35]
    warped = map_coordinates(base, coords, order=3, mode="mirror")
    return gaussian_filter(warped, 2.0)


def line_mask(z):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    levels = np.linspace(z.min(), z.max(), 34)
    ax.contour(z, levels=levels, colors="k", linewidths=1.1, origin="upper",
               extent=(0, W, H, 0), antialiased=True)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, transparent=True)
    plt.close(fig)
    rgba = np.asarray(Image.open(buf).convert("RGBA").resize((W, H)))
    return rgba[..., 3] / 255.0


def fade(w, h):
    # transparent behind the text column, rising towards the right edge
    x = np.linspace(0, 1, w)
    t = np.clip((x - 0.30) / 0.60, 0, 1)
    ramp = t * t * (3 - 2 * t)
    y = np.linspace(0, 1, h)[:, None]
    return ramp[None, :] * (0.85 + 0.15 * np.sin(np.pi * y))


def render(seed, bg, line, peak):
    z = field(seed)
    a = line_mask(z) * fade(W, H) * peak
    out = hex_rgb(bg) * (1 - a[..., None]) + hex_rgb(line) * a[..., None]
    return Image.fromarray(out.round().astype(np.uint8), "RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (sid, (bg, line, peak)) in enumerate(SLIDES.items()):
        img = render(1000 + i * 17, bg, line, peak)
        path = OUT / f"tex-{sid}.png"
        img.save(path, optimize=True)
        print(path.name, path.stat().st_size // 1024, "KB")
