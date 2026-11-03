"""Make the command line's and the library's banner scenes from the home page's.

Run it from the repository's root:

    uv run --no-project python brand/scenes.py

It reads ``site/assets/hero.svg`` and ``hero-small.svg`` and writes
``hero-cli*.svg`` and ``hero-library*.svg`` beside them. Copy those into the
command line's and the library's ``docs/assets``.

The scenes keep the home page's pixel style, ground and anvil, and change the
rest: the command line's world is drawn in a terminal's green, with a command
typing itself across the sky; the library's is sunrise, with a house being
built block by block.
"""

import re
from collections.abc import Callable
from pathlib import Path

ASSETS = Path(__file__).parent.parent / "site" / "assets"
SKY = re.compile(r'<linearGradient id="sky".*?</linearGradient>', re.S)
GLOW = re.compile(r'<radialGradient id="glow">.*?</radialGradient>', re.S)
FILL = re.compile(r'fill="#([0-9a-fA-F]{6})"')
STAR = re.compile(r'(<rect [^>]*fill="#ffffff" opacity=")([\d.]+)(")')


def rect(x: float, y: float, w: float, h: float, fill: str, extra: str = "") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def gradient(top: str, middle: str, bottom: str) -> str:
    return (
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/>'
        f'<stop offset="0.55" stop-color="{middle}"/>'
        f'<stop offset="0.8" stop-color="{bottom}"/>'
        "</linearGradient>"
    )


def glow(colour: str, opacity: float) -> str:
    return (
        '<radialGradient id="glow">'
        f'<stop offset="0" stop-color="{colour}" stop-opacity="{opacity}"/>'
        f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/>'
        "</radialGradient>"
    )


# The command line: everything in a terminal's green.

PHOSPHOR = [
    "#040a06", "#08160c", "#0c2413", "#11351b", "#174a25",
    "#1f6430", "#2c823d", "#3fa64f", "#62c96f", "#a6efae",
]


def phosphor(hex_colour: str) -> str:
    """Map a colour to the green of the same brightness."""
    r, g, b = (int(hex_colour[i : i + 2], 16) for i in (0, 2, 4))
    light = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return PHOSPHOR[min(len(PHOSPHOR) - 1, round(light ** 0.75 * (len(PHOSPHOR) - 1) * 1.25))]


# A 5 by 7 pixel font, for the few letters the command needs.
GLYPHS = {
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    " ": ["....."] * 7,
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "t": [".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."],
    "h": ["#....", "#....", "#.##.", "##..#", "#...#", "#...#", "#...#"],
}


def typed_command(text: str, x: int, y: int, size: int) -> str:
    """Draw a command in the pixel font; each letter appears in turn, in a loop."""
    parts = []
    for index, char in enumerate(text):
        cells = "".join(
            rect(x + index * 6 * size + col * size, y + row * size, size, size, "#a6efae")
            for row, line in enumerate(GLYPHS[char])
            for col, on in enumerate(line)
            if on == "#"
        )
        parts.append(f'<g class="key" style="animation-delay:{0.4 + index * 0.18:.2f}s">{cells}</g>')
    end = x + len(text) * 6 * size
    parts.append(f'<g class="cursor">{rect(end, y, size * 5, size * 7, "#a6efae")}</g>')
    # Lines of output that print after the command, as bars of text.
    widths = [(0, 300, "#62c96f"), (2, 380, "#2c823d"), (2, 340, "#2c823d"), (0, 260, "#a6efae")]
    for row, (indent, width, colour) in enumerate(widths):
        top = y + 7 * size + 40 + row * 34
        delay = 0.4 + len(text) * 0.18 + 0.5 + row * 0.35
        parts.append(
            f'<g class="key" style="animation-delay:{delay:.2f}s">'
            f'{rect(x + indent * size * 6, top, width, size * 2, colour)}</g>'
        )
    return "".join(parts)


# The moon's colours; the command line's sky has the command instead.
MOON = re.compile(r'<rect [^>]*fill="#(?:dfe4ec|c3cad6)"[^>]*/>')


def cli(text: str) -> str:
    text = MOON.sub("", text)
    text = SKY.sub(gradient("#020604", "#040b07", "#07140b"), text, count=1)
    text = GLOW.sub(glow("#3fa64f", 0.28), text, count=1)
    text = FILL.sub(lambda m: f'fill="{phosphor(m[1])}"', text)
    text = text.replace(
        "</defs>",
        '<pattern id="scan" width="8" height="8" patternUnits="userSpaceOnUse">'
        '<rect width="8" height="4" fill="#000000" opacity="0.22"/></pattern>'
        '<radialGradient id="vignette" cx="0.6" cy="0.55" r="0.75">'
        '<stop offset="0.55" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.55"/></radialGradient>'
        "</defs>",
        1,
    )
    style = (
        ".key{opacity:0;animation:key 9s steps(1) infinite}"
        "@keyframes key{0%{opacity:0}2%{opacity:1}90%{opacity:1}94%{opacity:0}}"
        ".cursor{animation:blink 1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.key{animation:none;opacity:1}.cursor{animation:none}}"
    )
    text = text.replace("</style>", style + "</style>", 1)
    overlay = (
        typed_command("$ modsmith", 1180, 150, 10)
        + rect(0, 0, 1920, 1080, "url(#scan)")
        + rect(0, 0, 1920, 1080, "url(#vignette)")
    )
    return text.replace("</svg>", overlay + "</svg>", 1)


# The library: sunrise, and a house going up block by block.

BLOCK = 30
STONE, PLANKS, LOG, GLASS, ROOF, DOOR = (
    "#8e8e8e", "#c69a5b", "#6b4a2b", "#9fd3e6", "#7a3b2e", "#5c3d24",
)


def house(x: int, ground: int) -> str:
    """A small house, 5 blocks wide, whose blocks drop into place in order."""
    layout = [
        # Rows from the ground up; each letter is one block.
        "SSSSS",
        "LPDPL",
        "LGDGL",
        "LPPPL",
        "RRRRRRR",
        ".RRRRR.",
        "..RRR..",
    ]
    colours = {"S": STONE, "P": PLANKS, "L": LOG, "G": GLASS, "D": DOOR, "R": ROOF}
    parts = []
    order = 0
    for row, line in enumerate(layout):
        offset = (len(line) - 5) // 2
        for col, key in enumerate(line):
            if key == ".":
                continue
            bx = x + (col - offset) * BLOCK
            by = ground - (row + 1) * BLOCK
            edge = rect(bx, by, BLOCK, BLOCK, "#1c1c20")
            face = rect(bx + 2, by + 2, BLOCK - 4, BLOCK - 4, colours[key])
            shine = rect(bx + 2, by + 2, BLOCK - 4, 4, "#ffffff", ' opacity="0.18"')
            parts.append(
                f'<g class="place" style="animation-delay:{0.3 + order * 0.2:.2f}s">{edge}{face}{shine}</g>'
            )
            order += 1
    return "".join(parts)


def floating(x: int, y: int, colour: str, delay: float) -> str:
    cells = rect(x, y, BLOCK, BLOCK, "#1c1c20") + rect(x + 2, y + 2, BLOCK - 4, BLOCK - 4, colour)
    return f'<g class="drift" style="animation-delay:{delay}s">{cells}</g>'


def library(text: str) -> str:
    text = SKY.sub(gradient("#1b2547", "#7a4f73", "#e8925a"), text, count=1)
    text = GLOW.sub(glow("#ffb45e", 0.38), text, count=1)
    # The moon becomes the rising sun.
    text = text.replace('fill="#dfe4ec"', 'fill="#ffd89a"').replace('fill="#c3cad6"', 'fill="#ffc46b"')
    text = STAR.sub(lambda m: f"{m[1]}{float(m[2]) * 0.3:.2f}{m[3]}", text)
    style = (
        ".place{opacity:0;animation:place 11s ease-out infinite}"
        "@keyframes place{0%{opacity:0;transform:translateY(-60px)}5%{opacity:1;transform:none}"
        "88%{opacity:1;transform:none}96%{opacity:0;transform:none}100%{opacity:0}}"
        ".drift{animation:drift 4s ease-in-out infinite alternate}"
        "@keyframes drift{to{transform:translateY(-16px)}}"
        "@media (prefers-reduced-motion:reduce){.place{animation:none;opacity:1}.drift{animation:none}}"
    )
    text = text.replace("</style>", style + "</style>", 1)
    overlay = (
        house(1620, 870)
        + floating(1700, 520, PLANKS, 0)
        + floating(1780, 470, STONE, 1.2)
        + floating(1600, 470, GLASS, 2.4)
    )
    return text.replace("</svg>", overlay + "</svg>", 1)


VARIANTS: dict[str, tuple[str, Callable[[str], str]]] = {
    "cli": ("A terminal's green world, with a command typing itself above an anvil", cli),
    "library": ("A house being built block by block beside an anvil at sunrise", library),
}


def make(source: Path, name: str) -> Path:
    label, build = VARIANTS[name]
    text = build(source.read_text(encoding="utf-8"))
    text = re.sub(r'aria-label="[^"]*"', f'aria-label="{label}"', text, count=1)
    out = source.with_name(source.name.replace("hero", f"hero-{name}"))
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


if __name__ == "__main__":
    for source in (ASSETS / "hero.svg", ASSETS / "hero-small.svg"):
        for name in VARIANTS:
            print(make(source, name))
