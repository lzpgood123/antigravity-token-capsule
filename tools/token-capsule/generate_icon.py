import os
from PIL import Image, ImageDraw

def create_capsule_image(size):
    w, h = size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    
    pad = int(w * 0.1)
    x0, y0 = pad, pad
    x1, y1 = w - pad, h - pad
    r = int((y1 - y0) / 2)
    
    mask = Image.new('L', (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=255)
    
    content = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(content)
    
    mid_x = w // 2
    # 左侧翡翠绿 (#10b981)
    cdraw.rectangle([0, 0, mid_x, h], fill=(16, 185, 129, 255))
    # 右侧宝石蓝 (#3b82f6)
    cdraw.rectangle([mid_x, 0, w, h], fill=(59, 130, 246, 255))
    
    # 顶部微拟物高光
    gloss_h = max(int(h * 0.18), 2)
    cdraw.rounded_rectangle([x0 + r//2, y0 + int(h*0.06), x1 - r//2, y0 + gloss_h], radius=gloss_h//2, fill=(255, 255, 255, 90))
    
    return Image.composite(content, img, mask)

def main():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [create_capsule_image((s, s)) for s in sizes]
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(curr_dir, 'capsule.ico')
    images[-1].save(out_path, format='ICO', sizes=[(s, s) for s in sizes])
    print(f'Successfully generated {out_path}')

if __name__ == '__main__':
    main()
