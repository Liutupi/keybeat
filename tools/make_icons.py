"""Draw the KEYBEAT app icon: a glowing keycap with a K on a dark field. usage: make_icons.py <out dir>"""
import sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
S = 1024
def icon(pad):
    im = Image.new("RGB", (S, S), "#0a0b13"); px = im.load()
    for y in range(S):                       # soft top-lit background
        for x in range(0, S):
            d = ((x - S / 2) ** 2 + (y - S * .3) ** 2) ** .5 / (S * .75); t = max(0, 1 - d)
            px[x, y] = (int(10 + 16 * t), int(11 + 16 * t), int(19 + 30 * t))
    k0, k1 = S * pad, S * (1 - pad); r = (k1 - k0) * .24
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    g.rounded_rectangle([k0, k0, k1, k1], r, outline=(124, 240, 255, 255), width=int(S * .045))
    im.paste(glow.filter(ImageFilter.GaussianBlur(S * .035)), (0, 0), glow.filter(ImageFilter.GaussianBlur(S * .035)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([k0, k0, k1, k1], r, fill="#12131f", outline="#7cf0ff", width=int(S * .022))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int((k1 - k0) * .62))
    bb = d.textbbox((0, 0), "K", font=f); w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((S / 2 - w / 2 - bb[0], S / 2 - h / 2 - bb[1] - (k1 - k0) * .03), "K", font=f, fill="#efecf6")
    bw = (k1 - k0) * .07; by = k1 - (k1 - k0) * .13                # beat marks under the letter
    for i, hgt in enumerate([.05, .09, .05]):
        cx = S / 2 + (i - 1) * bw * 1.9
        d.rounded_rectangle([cx - bw / 2, by - (k1 - k0) * hgt, cx + bw / 2, by], bw / 2, fill="#ffcf6b" if i == 1 else "#7cf0ff")
    return im
std, mask = icon(.17), icon(.25)
for name, src, size in [("icon-512.png", std, 512), ("icon-192.png", std, 192), ("icon-maskable-512.png", mask, 512), ("apple-touch-icon.png", std, 180), ("favicon-32.png", std, 32)]:
    src.resize((size, size), Image.LANCZOS).save(os.path.join(out, name), optimize=True)
print(os.listdir(out))
