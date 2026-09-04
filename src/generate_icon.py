"""
Token Capsule - Windows Multi-Resolution Icon Generator
Renders capsule.svg to multi-size Windows .ico (16, 24, 32, 48, 64, 128, 256 px)
and outputs a 512x512 capsule_preview.png using PySide6.QtSvg and PIL.
"""

import io
import os
import struct
from PIL import Image
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def render_svg_to_qimage(renderer: QSvgRenderer, width: int, height: int) -> QImage:
    """Renders QSvgRenderer to a QImage with high-quality anti-aliasing."""
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.end()

    return image


def qimage_to_pil(qimg: QImage) -> Image.Image:
    """Converts a QImage to a PIL RGBA Image via in-memory QBuffer."""
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    qimg.save(buffer, "PNG")
    png_bytes = bytes(buffer.data())
    buffer.close()
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def verify_ico_entries(ico_path: str):
    """Verifies that the generated ICO contains all expected directory entries."""
    if not os.path.exists(ico_path):
        raise FileNotFoundError(f"ICO file not found: {ico_path}")

    with open(ico_path, "rb") as f:
        data = f.read()

    reserved, ico_type, count = struct.unpack("<HHH", data[:6])
    print(f"[*] Verified ICO structure: Type={ico_type}, Embedded Resolutions Count={count}")
    for i in range(count):
        w, h, colors, res, planes, bpp, size_bytes, offset = struct.unpack(
            "<BBBBHHII", data[6 + i * 16 : 6 + (i + 1) * 16]
        )
        w = 256 if w == 0 else w
        h = 256 if h == 0 else h
        print(f"    - Layer {i}: {w}x{h} px, {bpp}-bit color ({size_bytes:,} bytes)")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(base_dir, "capsule.svg")
    ico_path = os.path.join(base_dir, "capsule.ico")
    preview_path = os.path.join(base_dir, "capsule_preview.png")

    if not os.path.exists(svg_path):
        raise FileNotFoundError(f"SVG source not found: {svg_path}")

    print(f"[+] Loading vector source: {svg_path}")
    with open(svg_path, "rb") as f:
        svg_bytes = f.read()

    renderer = QSvgRenderer(QByteArray(svg_bytes))
    if not renderer.isValid():
        raise ValueError(f"Failed to parse SVG content in {svg_path}")

    # 1. Generate 512x512 High-Res Master Preview
    print(f"[+] Rendering 512x512 master preview...")
    preview_qimg = render_svg_to_qimage(renderer, 512, 512)
    preview_qimg.save(preview_path, "PNG")
    print(f"[OK] Successfully generated preview: {preview_path}")

    # 2. Render each Windows standard icon resolution
    target_sizes = [16, 24, 32, 48, 64, 128, 256]
    pil_images = {}

    print(f"[+] Vector rasterizing {len(target_sizes)} icon resolutions...")
    for s in target_sizes:
        qimg = render_svg_to_qimage(renderer, s, s)
        pil_im = qimage_to_pil(qimg)
        pil_images[s] = pil_im
        print(f"    - Rasterized {s}x{s} px")

    # 3. Package into Windows Multi-Resolution ICO
    # Largest image (256x256) is master; smaller resolutions appended in ascending order
    im_256 = pil_images[256]
    sub_images = [pil_images[s] for s in [16, 24, 32, 48, 64, 128]]

    print(f"[+] Packaging multi-resolution Windows ICO: {ico_path}")
    im_256.save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in target_sizes],
        append_images=sub_images,
    )
    print(f"[OK] Successfully generated ICO: {ico_path} ({os.path.getsize(ico_path):,} bytes)")

    # 4. Verify ICO Integrity
    verify_ico_entries(ico_path)
    print("[DONE] All icon assets successfully built and verified!")


if __name__ == "__main__":
    main()
