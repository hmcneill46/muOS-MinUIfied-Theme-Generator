from pathlib import Path

from PIL import Image


def hex_to_rgba(hex_color: str | None, alpha=1.0) -> tuple[int, int, int, int]:
    # Convert hex to RGB
    if not hex_color:
        return (0, 0, 0, int(alpha * 255))

    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return (rgb[0], rgb[1], rgb[2], int(alpha * 255))


def rgb_to_hex(rgb_color: tuple[int, int, int]) -> str:
    # Convert RGB to hex
    return "{:02x}{:02x}{:02x}".format(*rgb_color)


def strip_hex_code(hex_code: str | None) -> str:
    # Strip the hash from a hex code
    return hex_code.lstrip("#") if hex_code else ""


def interpolate_color_component(c1: int, c2: int, factor: float) -> int:
    # Interpolate a single color component
    return int(c1 + (c2 - c1) * factor)


def percentage_color(hex1: str, hex2: str, percentage: float) -> str:
    # Convert hex colors to RGB
    rgb1 = hex_to_rgba(hex1)
    rgb2 = hex_to_rgba(hex2)

    # Calculate the interpolated color for each component
    interp_rgb = (
        interpolate_color_component(rgb1[0], rgb2[0], percentage),
        interpolate_color_component(rgb1[1], rgb2[1], percentage),
        interpolate_color_component(rgb1[2], rgb2[2], percentage),
    )

    # Convert interpolated RGB back to hex
    return rgb_to_hex(interp_rgb)


def change_logo_color(input: Path | Image.Image, hex_color) -> Image.Image:
    # Load the image
    if isinstance(input, Image.Image):
        img = input
    else:
        img = Image.open(input).convert("RGBA")

    # Convert hex_color to RGBA
    r, g, b, _ = hex_to_rgba(hex_color)

    alpha_image = img.split()[3]
    black_image = Image.new("RGBA", img.size, (0, 0, 0, 0))
    color_image = Image.new("RGBA", img.size, (r, g, b, 255))

    # Composite the color image with the alpha channel
    result_image = Image.composite(color_image, black_image, alpha_image)
    return result_image
