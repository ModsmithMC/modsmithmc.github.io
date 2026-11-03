"""Make each site's banner scene from the home page's, with its own sky and prop.

Run it from the repository's root:

    uv run --no-project python brand/scenes.py

It reads ``site/assets/hero.svg`` and ``hero-small.svg`` and writes
``hero-cli*.svg`` and ``hero-library*.svg`` beside them. Copy those into the
command line's and the library's ``docs/assets``.
"""

import re
from pathlib import Path

ASSETS = Path(__file__).parent.parent / "site" / "assets"
SKY = re.compile(r'(<linearGradient id="sky".*?</linearGradient>)', re.S)
STYLE_END = "</style>"
STAR = re.compile(r'(<rect [^>]*fill="#ffffff" opacity=")([\d.]+)(")')

PIXEL = 6  # One block of the props, in scene units.


def sky(top: str, middle: str, bottom: str) -> str:
    return (
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/>'
        f'<stop offset="0.55" stop-color="{middle}"/>'
        f'<stop offset="0.8" stop-color="{bottom}"/>'
        "</linearGradient>"
    )


def rect(x: float, y: float, w: float, h: float, fill: str, extra: str = "") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def terminal(x: int, y: int) -> str:
    """A floating terminal window whose lines type themselves in a loop."""
    w, h = 264, 168
    parts = [
        rect(x - PIXEL, y - PIXEL, w + 2 * PIXEL, h + 2 * PIXEL, "#1c1c20"),
        rect(x, y, w, h, "#0f1115"),
        rect(x, y, w, 24, "#22252b"),
    ]
    parts += [rect(x + 12 + i * 18, y + 9, PIXEL, PIXEL, "#3a3f48") for i in range(3)]
    lines = [
        # (indent, width, colour) of each line, as blocks of text.
        [(0, 12, "#6cc349"), (18, 150, "#d9dde3")],
        [(0, 120, "#8a909a")],
        [(12, 12, "#6cc349"), (30, 132, "#8a909a")],
        [(12, 12, "#6cc349"), (30, 102, "#8a909a")],
        [(0, 168, "#ffffff")],
    ]
    for row, blocks in enumerate(lines):
        top = y + 42 + row * 22
        cells = "".join(rect(x + 18 + dx, top, bw, PIXEL * 2, colour) for dx, bw, colour in blocks)
        parts.append(f'<g class="line" style="animation-delay:{row * 0.45}s">{cells}</g>')
    parts.append(f'<g class="cursor">{rect(x + 18, y + 42 + len(lines) * 22, 12, PIXEL * 2, "#d9dde3")}</g>')
    # Drawn at a small size, then scaled about its corner; the float moves the outer group.
    scaled = f'<g transform="translate({x} {y}) scale(1.3) translate({-x} {-y})">{"".join(parts)}</g>'
    return f'<g class="float">{scaled}</g>'


BLOCKS = {
    # Each block is 8 by 8 pixels: a top colour band, and a body with speckles.
    "grass": ("#52a535", "#3c8527", "#7a5233", "#5c3d24"),
    "stone": ("#8e8e8e", "#7a7a7a", "#8e8e8e", "#6a6a6a"),
    "planks": ("#c69a5b", "#a87c42", "#c69a5b", "#9a6f39"),
}


def block(x: int, y: int, kind: str, delay: float) -> str:
    """A floating Minecraft-style block, drawn pixel by pixel."""
    top, top_dark, body, body_dark = BLOCKS[kind]
    size = 9  # scene units per pixel
    parts = [rect(x - 3, y - 3, 8 * size + 6, 8 * size + 6, "#1c1c20")]
    for row in range(8):
        for col in range(8):
            band = row < 2 if kind == "grass" else False
            speckle = (row * 3 + col * 5 + len(kind)) % 7 == 0
            if kind == "planks" and row in (2, 5):
                colour = body_dark
            elif band:
                colour = top_dark if speckle else top
            else:
                colour = body_dark if speckle else body
            parts.append(rect(x + col * size, y + row * size, size, size, colour))
    return f'<g class="float" style="animation-delay:{delay}s">{"".join(parts)}</g>'


ANIMATION = {
    "cli": (
        ".float{animation:bob 5s ease-in-out infinite alternate}"
        "@keyframes bob{to{transform:translateY(-14px)}}"
        ".line{opacity:0;animation:type 6s steps(1) infinite}"
        "@keyframes type{0%{opacity:0}8%{opacity:1}85%{opacity:1}100%{opacity:0}}"
        ".cursor{animation:blink 1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.float,.line,.cursor{animation:none;opacity:1}}"
    ),
    "library": (
        ".float{animation:bob 4s ease-in-out infinite alternate}"
        "@keyframes bob{to{transform:translateY(-18px)}}"
        "@media (prefers-reduced-motion:reduce){.float{animation:none}}"
    ),
}
VARIANTS = {
    "cli": {
        "label": "A terminal window floating beside an anvil at dusk",
        "sky": sky("#140f22", "#2a1c33", "#4a2a30"),
        "stars": 0.6,
        "props": lambda: terminal(1540, 150),
    },
    "library": {
        "label": "Blocks floating beside an anvil at twilight",
        "sky": sky("#0a1222", "#0f2138", "#173349"),
        "stars": 1.0,
        "props": lambda: (
            block(1640, 200, "grass", 0)
            + block(1790, 330, "stone", 1.3)
            + block(1110, 250, "planks", 2.6)
        ),
    },
}


def make(source: Path, name: str) -> Path:
    variant = VARIANTS[name]
    text = source.read_text(encoding="utf-8")
    text, count = SKY.subn(variant["sky"], text, count=1)
    assert count == 1, f"{source} has no sky gradient"
    text = re.sub(r'aria-label="[^"]*"', f'aria-label="{variant["label"]}"', text, count=1)
    text = text.replace(STYLE_END, ANIMATION[name] + STYLE_END, 1)
    scale = variant["stars"]
    text = STAR.sub(lambda m: f"{m[1]}{float(m[2]) * scale:.2f}{m[3]}", text)
    # Props go above the sky and stars, and behind the glow, anvil and ground.
    glow = text.index("<circle")
    text = text[:glow] + variant["props"]() + text[glow:]
    out = source.with_name(source.name.replace("hero", f"hero-{name}"))
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    for source in (ASSETS / "hero.svg", ASSETS / "hero-small.svg"):
        for name in VARIANTS:
            print(make(source, name))
