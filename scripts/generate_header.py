#!/usr/bin/env python3
"""Generate the original BishopDGreat GitHub profile header animation."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1200, 420
FRAME_COUNT = 64
DURATION_MS = 100
CENTER = (265, 210)
BG_TOP = (6, 8, 20)
BG_BOTTOM = (12, 12, 34)
VIOLET = (126, 91, 255)
CYAN = (97, 219, 251)
GOLD = (238, 190, 92)
SILVER = (232, 236, 246)
MUTED = (153, 162, 184)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

TITLE = ImageFont.truetype(FONT_BOLD, 64)
SUBTITLE = ImageFont.truetype(FONT_REGULAR, 25)
MONO = ImageFont.truetype(FONT_MONO, 18)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease(value: float) -> float:
    value = clamp(value)
    return 1 - (1 - value) ** 3


def background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()
    rng = random.Random(7341)
    stars = {(rng.randrange(WIDTH), rng.randrange(HEIGHT)): rng.randrange(5, 18) for _ in range(115)}
    for y in range(HEIGHT):
        mix = y / (HEIGHT - 1)
        row = tuple(round(BG_TOP[i] * (1 - mix) + BG_BOTTOM[i] * mix) for i in range(3))
        for x in range(WIDTH):
            vignette = ((x - WIDTH / 2) / (WIDTH / 2)) ** 2 + ((y - HEIGHT / 2) / (HEIGHT / 2)) ** 2
            shade = max(0.7, 1 - vignette * 0.16)
            star = stars.get((x, y), 0)
            pixels[x, y] = tuple(min(255, round(channel * shade) + star) for channel in row)
    return image


BASE = background()


def glowing_line(layer: Image.Image, points: list[tuple[float, float]], color: tuple[int, int, int], alpha: int) -> None:
    if len(points) < 2 or alpha <= 0:
        return
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(points, fill=(*color, max(1, alpha // 4)), width=30, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    layer.alpha_composite(glow)
    draw = ImageDraw.Draw(layer)
    draw.line(points, fill=(*color, max(1, alpha // 2)), width=8, joint="curve")
    draw.line(points, fill=(245, 247, 255, alpha), width=2, joint="curve")


def segment(start: tuple[int, int], end: tuple[int, int], progress: float) -> list[tuple[float, float]]:
    progress = ease(progress)
    return [start, (start[0] + (end[0] - start[0]) * progress, start[1] + (end[1] - start[1]) * progress)]


def frame(index: int) -> Image.Image:
    t = index / (FRAME_COUNT - 1)
    image = BASE.convert("RGBA")
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # The four fragments converge independently rather than tracing one outline.
    assemble = ease(t / 0.34)
    hold = clamp((0.82 - t) / 0.12)
    cross_alpha = round(255 * min(assemble, hold if t > 0.70 else 1))
    cx, cy = CENTER
    horizontal = 112
    vertical = 142
    gap = 16

    arms = [
        ((cx - 250, cy), (cx - gap, cy), CYAN),
        ((cx + 250, cy), (cx + gap, cy), VIOLET),
        ((cx, cy - 255), (cx, cy - gap), VIOLET),
        ((cx, cy + 255), (cx, cy + gap), CYAN),
    ]
    endpoints = [
        (cx - horizontal, cy),
        (cx + horizontal, cy),
        (cx, cy - vertical),
        (cx, cy + vertical),
    ]

    for (origin, _target, color), endpoint in zip(arms, endpoints):
        start = (
            origin[0] + (endpoint[0] - origin[0]) * assemble,
            origin[1] + (endpoint[1] - origin[1]) * assemble,
        )
        glowing_line(layer, segment(start, (cx, cy), assemble), color, cross_alpha)

    # Circuit branches make the mark a technical symbol rather than a medical emblem.
    branch_progress = ease((t - 0.18) / 0.20)
    branches = [
        [(cx - 94, cy), (cx - 94, cy - 34), (cx - 68, cy - 34)],
        [(cx + 94, cy), (cx + 94, cy + 34), (cx + 68, cy + 34)],
        [(cx, cy - 116), (cx + 30, cy - 116), (cx + 30, cy - 92)],
        [(cx, cy + 116), (cx - 30, cy + 116), (cx - 30, cy + 92)],
    ]
    for idx, points in enumerate(branches):
        if branch_progress > idx * 0.12:
            glowing_line(layer, points, GOLD if idx % 2 else VIOLET, round(cross_alpha * 0.72))
            px, py = points[-1]
            radius = 3 + 2 * math.sin(index * 0.35 + idx)
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*GOLD, cross_alpha))

    # Restrained center pulse.
    pulse = 0.5 + 0.5 * math.sin(index * math.pi / 8)
    if assemble > 0.75 and cross_alpha > 0:
        radius = 8 + pulse * 8
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse(
            (cx - radius * 3, cy - radius * 3, cx + radius * 3, cy + radius * 3),
            fill=(*GOLD, round(55 * cross_alpha / 255)),
        )
        halo = halo.filter(ImageFilter.GaussianBlur(16))
        layer.alpha_composite(halo)
        draw.ellipse((cx - radius / 2, cy - radius / 2, cx + radius / 2, cy + radius / 2), fill=(*GOLD, cross_alpha))

    image.alpha_composite(layer)

    # Name resolves from left to right after the mark assembles.
    text_progress = ease((t - 0.24) / 0.22)
    fade_out = clamp((0.92 - t) / 0.10)
    text_alpha = round(255 * min(text_progress, fade_out))
    tx, ty = 455, 135
    text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    td.text((tx, ty), "BishopDGreat", font=TITLE, fill=(*SILVER, text_alpha))
    td.text((tx + 3, ty + 82), "EMMANUEL NWACHINEMERE  ·  FULL-STACK DEVELOPER", font=MONO, fill=(*GOLD, text_alpha))
    td.text((tx + 3, ty + 122), "frontend / backend / data / problem-solving", font=SUBTITLE, fill=(*MUTED, text_alpha))
    reveal_width = round(720 * text_progress)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rectangle((tx - 8, 90, tx + reveal_width, 330), fill=text_alpha)
    text_layer.putalpha(Image.composite(text_layer.getchannel("A"), Image.new("L", image.size, 0), mask))
    image.alpha_composite(text_layer)

    # Dissolve into deterministic data nodes at the end of the loop.
    dissolve = ease((t - 0.78) / 0.18)
    if dissolve > 0:
        particles = Image.new("RGBA", image.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(particles)
        rng = random.Random(9817)
        for i in range(44):
            angle = rng.random() * math.tau
            distance = (20 + rng.random() * 150) * dissolve
            px = cx + math.cos(angle) * distance
            py = cy + math.sin(angle) * distance
            radius = 1 + rng.random() * 2
            color = GOLD if i % 4 == 0 else (CYAN if i % 2 else VIOLET)
            particle_alpha = round(210 * ((1 - dissolve) ** 1.4))
            pd.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(*color, particle_alpha))
        image.alpha_composite(particles)

    return image.convert("RGB")


def main() -> None:
    generated = [frame(i) for i in range(FRAME_COUNT)]
    # Start on the complete identity so GitHub never presents a blank first impression.
    # The loop then dissolves, rebuilds, and ends on the same complete frame.
    rotation_index = 30
    frames = generated[rotation_index:] + generated[: rotation_index + 1]
    output = ASSETS / "header.gif"
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"generated={output}")
    print(f"frames={len(frames)}")
    print(f"duration_seconds={len(frames) * DURATION_MS / 1000:.1f}")
    print(f"bytes={output.stat().st_size}")


if __name__ == "__main__":
    main()
