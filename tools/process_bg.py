"""Turn GPT background drafts into game layers. usage: process_bg.py <far.png> <near.png> <out dir>"""
import sys, os
import numpy as np
from PIL import Image
far_p, near_p, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
H = 512

def period(a, lo, hi):
    """Horizontal repeat period of an RGB array, searched in [lo, hi)."""
    g = a.mean(axis=2)
    best, bp = 1e9, None
    for p in range(lo, hi):
        d = np.abs(g[:, :g.shape[1] - p] - g[:, p:]).mean()
        if d < best: best, bp = d, p
    return bp, best

# far layer: opaque, crop to one exact repeat when the art repeats, else keep whole
f = np.asarray(Image.open(far_p).convert("RGB")).astype(np.int16)
w = f.shape[1]; p, err = period(f, w // 3, w - 40)
fx = f[:, :p] if err < 3 else f
Image.fromarray(fx.astype(np.uint8)).resize((round(fx.shape[1] * H / fx.shape[0]), H), Image.LANCZOS) \
    .quantize(64, dither=Image.Dither.NONE).save(os.path.join(out, "bg-far.png"), optimize=True)
print("far: period", p, "err", round(float(err), 2), "->", "cropped" if err < 3 else "kept whole")

# near layer: key out green, crop one repeat, drop empty rows under the buildings so they stand on the ground
n = np.asarray(Image.open(near_p).convert("RGB")).astype(np.int16)
r, g, b = n[..., 0], n[..., 1], n[..., 2]
greenness = g - np.maximum(r, b)                       # >0 means greenish
alpha = np.clip(255 - (greenness - 40) * 4, 0, 255).astype(np.uint8)   # soft edge
spill = greenness > 0
n2 = n.copy(); n2[..., 1] = np.where(spill, np.maximum(r, b), g)      # remove green fringe
w = n.shape[1]; p, err = period(n, w // 3, w - 40)
sl = slice(0, p) if err < 6 else slice(0, w)
rgba = np.dstack([n2[:, sl].astype(np.uint8), alpha[:, sl]])
rows = np.where(rgba[..., 3].max(axis=1) > 30)[0]
rgba = rgba[rows[0]:rows[-1] + 1] if len(rows) else rgba
# pad back on top so the layer keeps its original sky proportion above the skyline
top = rows[0] if len(rows) else 0
canvas = np.zeros((rgba.shape[0] + top, rgba.shape[1], 4), np.uint8); canvas[top:] = rgba
im = Image.fromarray(canvas, "RGBA")
im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
im.save(os.path.join(out, "bg-near.png"), optimize=True)
print("near: period", p, "err", round(float(err), 2), "cut empty rows below", n.shape[0] - 1 - rows[-1], "final", im.size)
for k in ("bg-far.png", "bg-near.png"): print(k, os.path.getsize(os.path.join(out, k)) // 1024, "KB")
