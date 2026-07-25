#!/usr/bin/env python3
"""PR #1818 健康 row 截图：用基线存档的 ANSI 输出合成 cast，agg 渲染，抽末帧 PNG。"""

import json
import os
import subprocess
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
BASE = "/Users/quejianming/vscode/cosh-shell-dev/artifacts/banner-green-quiet-baseline-20260725"

SHOTS = [
    ("healthy-row-en-after", os.path.join(BASE, "pass-output.txt")),
    ("healthy-row-zh-after", os.path.join(BASE, "pass-output-zh.txt")),
    ("healthy-quiet-before", os.path.join(BASE, "fail-output.txt")),
]

COLS, ROWS = 102, 24


def make_cast(name, source):
    with open(source, "rb") as f:
        data = f.read().decode("utf-8", errors="replace")
    # 只保留启动卡片段，去掉退出回显噪声
    cast_path = os.path.join(OUT, f"{name}.cast")
    with open(cast_path, "w") as f:
        f.write(json.dumps({"version": 2, "width": COLS, "height": ROWS}) + "\n")
        f.write(json.dumps([0.1, "o", data.replace("\n", "\r\n")]) + "\n")
    return cast_path


def render(name, cast_path):
    gif = os.path.join(OUT, f"{name}.gif")
    png = os.path.join(OUT, f"{name}.png")
    subprocess.run(["agg", "--last-frame-duration", "1", cast_path, gif], check=True)
    subprocess.run(
        [sys.executable, "-c",
         "import sys; from PIL import Image, ImageSequence; "
         "im = Image.open(sys.argv[1]); "
         "frames = list(ImageSequence.Iterator(im)); "
         "frames[-1].convert('RGB').save(sys.argv[2])",
         gif, png],
        check=True,
    )
    os.unlink(gif)
    os.unlink(cast_path)
    print(f"wrote {png}")


for name, source in SHOTS:
    render(name, make_cast(name, source))
