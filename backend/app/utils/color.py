def hex_to_bgr(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)

    return (b, g, r)
