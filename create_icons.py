import os
from PIL import Image, ImageDraw  # type: ignore[missing-import]

def draw_icon(size: Any) -> None:  # type: ignore[unknown-name]
    scale = size / 128.0
    # Create image with maroon background (#7B1A2E)
    img = Image.new('RGB', (size, size), color=(123, 26, 46))
    draw = ImageDraw.Draw(img)
    
    # Gold circle in the middle (#C9A84C)
    r = int(26 * scale)
    cx = int(64 * scale)
    cy = int(58 * scale)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(201, 168, 76))
    
    # White smile path at the bottom (#FFFFFF)
    # in 128x128 grid: left=50, right=92, top=74, bottom=94
    left = int(50 * scale)
    right = int(92 * scale)
    top = int(74 * scale)
    bottom = int(94 * scale)
    stroke_width = max(2, int(8 * scale))
    
    draw.arc([left, top, right, bottom], start=0, end=180, fill=(255, 255, 255), width=stroke_width)
    
    return img  # type: ignore[BSK-E0013]

if __name__ == '__main__':
    os.makedirs('app/static/images', exist_ok=True)
    draw_icon(192).save('icon-192.png')
    draw_icon(512).save('icon-512.png')
    draw_icon(192).save('app/static/images/icon-192.png')
    draw_icon(512).save('app/static/images/icon-512.png')
    print("PNG Icons generated successfully in root and app/static/images!")
