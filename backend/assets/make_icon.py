# -*- coding: utf-8 -*-
"""生成应用图标：画一个废纸篓，导出 1024px PNG（再由 build 脚本转成 .icns）。"""

from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 1024
OUT = Path(__file__).resolve().parent / "icon_1024.png"

BODY = (142, 142, 147, 255)
BODY_DARK = (99, 99, 104, 255)
SLOT = (60, 60, 65, 255)
HIGHLIGHT = (200, 200, 205, 255)


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def main():
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 桶盖
    rounded(draw, (250, 236, 774, 300), 30, BODY_DARK)
    # 提手
    draw.arc((400, 150, 624, 330), start=180, end=360, fill=BODY_DARK, width=34)

    # 桶身（上宽下窄的梯形，用多边形画）
    body = [(296, 300), (728, 300), (676, 800), (348, 800)]
    draw.polygon(body, fill=BODY)

    # 桶身左侧高光
    draw.polygon([(296, 300), (356, 300), (392, 800), (348, 800)], fill=HIGHLIGHT)

    # 桶内竖条
    for offset in (0, 1, 2):
        x = 420 + offset * 92
        draw.rounded_rectangle(
            (x, 400, x + 44, 720), radius=20, fill=SLOT
        )

    # 桶底
    rounded(draw, (330, 786, 694, 838), 26, BODY_DARK)

    image.save(OUT)
    print(f"图标已生成: {OUT}")


if __name__ == "__main__":
    main()
