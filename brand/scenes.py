"""Make the command line's and the library's banner scenes from the home page's.

Run it from the repository's root:

    uv run --no-project --with fonttools --with brotli python brand/scenes.py

It reads ``site/assets/hero.svg`` and ``hero-small.svg`` and writes
``hero-cli*.svg`` and ``hero-library*.svg`` beside them, a README banner for
each site (``banner*.svg``), and the repositories' preview cards
(``brand/social-*.svg``). Copy each site's hero and banner into the command
line's and the library's ``docs/assets``, the banner as ``banner.svg``.

The scenes keep the home page's pixel style, ground and anvil, and change the
rest: the command line's world is drawn in a terminal's green, with a command
typing itself across the sky; the library's is sunrise, with materials flying
onto the anvil and a new tool rising from it.
"""

import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

BRAND = Path(__file__).parent
ASSETS = BRAND.parent / "site" / "assets"
SKY = re.compile(r'<linearGradient id="sky".*?</linearGradient>', re.DOTALL)
GLOW = re.compile(r'<radialGradient id="glow">.*?</radialGradient>', re.DOTALL)
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
    "#040a06",
    "#08160c",
    "#0c2413",
    "#11351b",
    "#174a25",
    "#1f6430",
    "#2c823d",
    "#3fa64f",
    "#62c96f",
    "#a6efae",
]


def phosphor(hex_colour: str) -> str:
    """Map a colour to the green of the same brightness."""
    r, g, b = (int(hex_colour[i : i + 2], 16) for i in (0, 2, 4))
    light = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return PHOSPHOR[
        min(len(PHOSPHOR) - 1, round(light**0.75 * (len(PHOSPHOR) - 1) * 1.25))
    ]


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
            rect(
                x + index * 6 * size + col * size, y + row * size, size, size, "#a6efae"
            )
            for row, line in enumerate(GLYPHS[char])
            for col, on in enumerate(line)
            if on == "#"
        )
        parts.append(
            f'<g class="key" style="animation-delay:{0.4 + index * 0.18:.2f}s">{cells}</g>'
        )
    end = x + len(text) * 6 * size
    parts.append(f'<g class="cursor">{rect(end, y, size * 5, size * 7, "#a6efae")}</g>')
    # Lines of output that print after the command, as bars of text.
    widths = [
        (0, 300, "#62c96f"),
        (2, 380, "#2c823d"),
        (2, 340, "#2c823d"),
        (0, 260, "#a6efae"),
    ]
    for row, (indent, width, colour) in enumerate(widths):
        top = y + 7 * size + 40 + row * 34
        delay = 0.4 + len(text) * 0.18 + 0.5 + row * 0.35
        parts.append(
            f'<g class="key" style="animation-delay:{delay:.2f}s">'
            f"{rect(x + indent * size * 6, top, width, size * 2, colour)}</g>"
        )
    return "".join(parts)


# The moon's colours; the command line's sky has the command instead.
MOON = re.compile(r'<rect [^>]*fill="#(?:dfe4ec|c3cad6)"[^>]*/>')

# Trees: leaves in two greens over a trunk of the same brown as the dirt.
TILE = re.compile(
    r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="[\d.]+" fill="#([0-9a-f]{6})"/>'
)
TRUNK, LEAVES = "3d2919", ("2a641c", "3c8527")


def tiles(text: str) -> dict[tuple[float, float], set[str]]:
    """The colours drawn at each tile of the scene."""
    cells: dict[tuple[float, float], set[str]] = {}
    for m in TILE.finditer(text):
        cells.setdefault((float(m[1]), float(m[2])), set()).add(m[4])
    return cells


def trunks(text: str) -> set[tuple[float, float]]:
    """Find the trunk tiles: brown columns that start among leaves."""
    cells = tiles(text)
    # The size most tiles have; a few larger shapes are drawn as rects too.
    size = float(Counter(m[3] for m in TILE.finditer(text)).most_common(1)[0][0])
    found = set()
    for (x, y), colours in cells.items():
        beside = cells.get((x - size, y), set()) | cells.get((x + size, y), set())
        if TRUNK not in colours or LEAVES[0] not in beside:
            continue
        while TRUNK in cells.get((x, y), set()) and not (
            TRUNK in cells.get((x - size, y), set())
            or TRUNK in cells.get((x + size, y), set())
        ):
            found.add((x, y))
            y += size
    return found


def recolour_tiles(
    text: str, where: set[tuple[float, float]], old: str, new: str
) -> str:
    """Give the tiles at these places a new colour where they have the old one."""

    def swap(m: re.Match[str]) -> str:
        here = (float(m[1]), float(m[2]))
        return m[0].replace(f"#{old}", new) if here in where and m[4] == old else m[0]

    return TILE.sub(swap, text)


def cli(text: str, prompt: tuple[int, int, int] = (1180, 150, 10)) -> str:
    text = MOON.sub("", text)
    text = SKY.sub(gradient("#020604", "#040b07", "#07140b"), text, count=1)
    text = GLOW.sub(glow("#3fa64f", 0.28), text, count=1)
    # In green, the trunks' brown is as dark as the hills behind them, so they
    # get a green of their own.
    text = recolour_tiles(text, trunks(text), TRUNK, "trunk")
    text = FILL.sub(lambda m: f'fill="{phosphor(m[1])}"', text)
    text = text.replace('fill="trunk"', 'fill="#1f6430"')
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
        typed_command("$ modsmith", *prompt)
        + rect(0, 0, 1920, 1080, "url(#scan)")
        + rect(0, 0, 1920, 1080, "url(#vignette)")
    )
    return text.replace("</svg>", overlay + "</svg>", 1)


# The library: sunrise, and things being made at the anvil.

PIXEL = 12  # One pixel of the item sprites, in scene units.
# Where materials land and the made item rises from: the anvil's hot face.
FORGE_X, FORGE_Y = 1453, 556

SPRITES = {
    # Each letter is one pixel; colours are below.
    "ingot": ["..LLLL", ".LWWWWL", "LMMMMMML", "DDDDDDDD"],
    "diamond": ["..C..", ".CWC.", "CCCCC", ".CBC.", "..C.."],
    "planks": ["PPPP", "QQQQ", "PPPP", "QQQQ"],
    "stick": ["...S", "..T.", ".S..", "T..."],
    "coal": [".KK.", "KGKK", "KKGK", ".KK."],
    "pickaxe": [
        "....CCCCC...",
        "..CCWWWCCB..",
        ".CCB...STCB.",
        ".CB...ST..CB",
        "CB...ST....B",
        "B...ST......",
        "...ST.......",
        "..ST........",
        ".ST.........",
        "ST..........",
    ],
}
SPRITE_COLOURS = {
    "L": "#e6e6e6",
    "W": "#ffffff",
    "M": "#b8b8b8",
    "D": "#7a7a7a",
    "C": "#4fd1d9",
    "B": "#2a9aa3",
    "P": "#c69a5b",
    "Q": "#a87c42",
    "S": "#9a6a35",
    "T": "#6b4423",
    "K": "#2b2b30",
    "G": "#55555e",
}


def sprite(name: str, x: float, y: float) -> str:
    """Draw a sprite with its top-left corner at x, y."""
    return "".join(
        rect(x + col * PIXEL, y + row * PIXEL, PIXEL, PIXEL, SPRITE_COLOURS[key])
        for row, line in enumerate(SPRITES[name])
        for col, key in enumerate(line)
        if key in SPRITE_COLOURS
    )


def centred(name: str) -> str:
    """Draw a sprite centred above the anvil's face, where it is made."""
    rows = SPRITES[name]
    width = max(len(line) for line in rows) * PIXEL
    height = len(rows) * PIXEL
    return sprite(name, FORGE_X - width / 2, FORGE_Y - height - 6)


# Materials fly in from the sky; each path is its offset from the anvil.
MATERIALS = [
    ("ingot", (420, -330), 0.0),
    ("diamond", (-520, -380), 0.3),
    ("stick", (120, -460), 0.6),
    ("planks", (300, -160), 0.9),
    ("coal", (-340, -220), 1.2),
]
LOOP = 8  # seconds


def forge_style(lift: int) -> str:
    """Keyframes for the materials, the flash, and the item that rises."""
    parts = []
    for name, (dx, dy), delay in MATERIALS:
        start = delay / LOOP * 100
        land = (delay + 1.4) / LOOP * 100
        parts.append(
            f"@keyframes in-{name}{{"
            f"0%,{start:.1f}%{{opacity:0;transform:translate({dx}px,{dy}px) rotate(-30deg)}}"
            f"{start + 2:.1f}%{{opacity:1}}"
            f"{(start + land) / 2:.1f}%{{transform:translate({dx * 0.45:.0f}px,{dy * 0.9:.0f}px) rotate(-10deg)}}"
            f"{land:.1f}%{{opacity:1;transform:translate(0,0)}}"
            f"{land + 1:.1f}%,100%{{opacity:0;transform:translate(0,0)}}}}"
            f".in-{name}{{animation:in-{name} {LOOP}s ease-in infinite}}"
        )
    parts.append(
        "@keyframes flash{0%,31%{opacity:0}35%{opacity:.9}48%,100%{opacity:0}}"
        f".flash{{opacity:0;animation:flash {LOOP}s ease-out infinite}}"
        "@keyframes made{0%,34%{opacity:0;transform:translateY(0) scale(.4)}"
        f"44%{{opacity:1;transform:translateY(-{lift - 10}px) scale(1)}}"
        f"50%{{transform:translateY(-{lift + 15}px) rotate(-8deg)}}"
        f"62%{{transform:translateY(-{lift - 5}px) rotate(4deg)}}"
        f"74%{{transform:translateY(-{lift + 15}px) rotate(-6deg)}}"
        f"84%{{opacity:1;transform:translateY(-{lift}px)}}"
        f"92%,100%{{opacity:0;transform:translateY(-{lift + 45}px)}}}}"
        f".made{{opacity:0;transform-box:fill-box;transform-origin:50% 100%;animation:made {LOOP}s ease-out infinite}}"
        "@media (prefers-reduced-motion:reduce){"
        + ",".join(f".in-{name}" for name, _, _ in MATERIALS)
        + ",.flash{animation:none;opacity:0}"
        f".made{{animation:none;opacity:1;transform:translateY(-{lift}px)}}}}"
    )
    return "".join(parts)


def library(text: str, lift: int = 180) -> str:
    text = SKY.sub(gradient("#1b2547", "#7a4f73", "#e8925a"), text, count=1)
    text = GLOW.sub(glow("#ffb45e", 0.38), text, count=1)
    # The moon becomes the rising sun.
    text = text.replace('fill="#dfe4ec"', 'fill="#ffd89a"').replace(
        'fill="#c3cad6"', 'fill="#ffc46b"'
    )
    text = STAR.sub(lambda m: f"{m[1]}{float(m[2]) * 0.3:.2f}{m[3]}", text)
    text = text.replace("</style>", forge_style(lift) + "</style>", 1)
    flash = (
        '<radialGradient id="flash"><stop offset="0" stop-color="#fff2c4" stop-opacity="1"/>'
        '<stop offset="1" stop-color="#ffb45e" stop-opacity="0"/></radialGradient>'
    )
    text = text.replace("</defs>", flash + "</defs>", 1)
    overlay = (
        "".join(f'<g class="in-{name}">{centred(name)}</g>' for name, _, _ in MATERIALS)
        + f'<circle class="flash" cx="{FORGE_X}" cy="{FORGE_Y - 20}" r="170" fill="url(#flash)"/>'
        + f'<g class="made">{centred("pickaxe")}</g>'
    )
    return text.replace("</svg>", overlay + "</svg>", 1)


VARIANTS: dict[str, tuple[str, Callable[[str], str]]] = {
    "cli": (
        "A terminal's green world, with a command typing itself above an anvil",
        cli,
    ),
    "library": (
        "Materials flying onto an anvil at sunrise, and a pickaxe rising from it",
        library,
    ),
}


def make(source: Path, name: str) -> Path:
    label, build = VARIANTS[name]
    text = build(source.read_text(encoding="utf-8"))
    text = re.sub(r'aria-label="[^"]*"', f'aria-label="{label}"', text, count=1)
    out = source.with_name(source.name.replace("hero", f"hero-{name}"))
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


# README banners and the repositories' preview cards: a scene framed wide,
# with the name and a line about the site. Text is drawn as paths, so the
# images look the same everywhere without loading a font.

FONTS = BRAND.parent / "theme" / "src" / "modsmith_sphinx_theme" / "modsmith" / "static"
FRAMES = {
    # name: (viewBox, width, height)
    "banner": ("0 300 1920 660", 1280, 440),
    "social": ("0 150 1920 960", 1280, 640),
}


@dataclass(frozen=True)
class Banner:
    scene: Callable[[str], str]  # Turns the home page's scene into this one.
    tagline: str
    name_colour: str
    tagline_colour: str
    outputs: dict[str, Path]  # Frame name to the file it is written to.


BANNERS = {
    "home": Banner(
        lambda text: text,
        "Modpacks, ready in the official launcher",
        "#ffffff",
        "#d3d7dc",
        {"banner": ASSETS / "banner.svg"},
    ),
    "cli": Banner(
        # The command types itself over the anvil, where the frame can see it.
        lambda text: cli(text, prompt=(1180, 330, 8)),
        "Modpacks from your terminal",
        "#a6efae",
        "#62c96f",
        {"banner": ASSETS / "banner-cli.svg", "social": BRAND / "social-modsmith.svg"},
    ),
    "library": Banner(
        lambda text: library(text, lift=100),
        "Build your own modpack tools",
        "#ffffff",
        "#ffe0bf",
        {
            "banner": ASSETS / "banner-library.svg",
            "social": BRAND / "social-modsmith-python.svg",
        },
    ),
}


def text_path(font: str, text: str, size: float, left: float, baseline: float) -> str:
    """Draw text in one of the theme's fonts as SVG path data."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    face = TTFont(FONTS / font)
    glyphs = face.getGlyphSet()
    cmap = face.getBestCmap()
    scale = size / face["head"].unitsPerEm
    pen = SVGPathPen(glyphs)
    # Line the first letter's ink up with the left edge.
    x = -face["hmtx"][cmap[ord(text[0])]][1]
    for char in text:
        glyph = glyphs[cmap[ord(char)]]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, left + x * scale, baseline)))
        x += glyph.width
    return pen.getCommands()


def without_left_trees(text: str) -> str:
    """Take out the two trees on the left, where the name and tagline go."""
    tree = (TRUNK, *LEAVES)

    def keep(m: re.Match[str]) -> str:
        behind_text = float(m[1]) < 600 and float(m[2]) < 840
        return "" if behind_text and m[4] in tree else m[0]

    return TILE.sub(keep, text)


def make_banner(banner: Banner) -> list[Path]:
    hero = (ASSETS / "hero.svg").read_text(encoding="utf-8")
    text = banner.scene(without_left_trees(hero))
    words = (
        f'<path fill="{banner.name_colour}" '
        f'd="{text_path("chakra-petch-700.woff2", "Modsmith", 168, 130.92, 660)}"/>'
        f'<path fill="{banner.tagline_colour}" '
        f'd="{text_path("chakra-petch-600.woff2", banner.tagline, 50, 127.5, 738)}"/>'
    )
    text = text.replace("</svg>", words + "</svg>", 1)
    written = []
    for frame, out in banner.outputs.items():
        view, width, height = FRAMES[frame]
        framed = text.replace(
            'viewBox="0 0 1920 1080"',
            f'viewBox="{view}" width="{width}" height="{height}"',
            1,
        )
        out.write_text(framed, encoding="utf-8", newline="\n")
        written.append(out)
    return written


if __name__ == "__main__":
    for source in (ASSETS / "hero.svg", ASSETS / "hero-small.svg"):
        for name in VARIANTS:
            print(make(source, name))
    for banner in BANNERS.values():
        for out in make_banner(banner):
            print(out)
