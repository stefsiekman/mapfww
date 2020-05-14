import time

from PIL import Image

from typing import List


def write_image(name, data: List[List[float]]):
    w = max(len(l) for l in data)
    h = len(data)
    scale = 100
    image = Image.new("RGBA", (w * scale, h * scale))

    pixels = [(0, 0, 0, 0)] * w * h * scale ** 2
    for y in range(h):
        for x in range(w):
            for sy in range(scale):
                for sx in range(scale):
                    value = data[y][x] if data is not None else 0
                    px = x * scale + sx
                    py = y * scale + sy
                    pixels[px + py * w * scale] = (
                    255, 255, 255, int(255 * value))

    image.putdata(pixels)
    label = time.strftime("%Y%m%d_%H%M%S")
    image.save(f"reports/report_{label}_{name}.png")


if __name__ == "__main__":
    write_image("test", [[1, 0], [0, 0.5]])
