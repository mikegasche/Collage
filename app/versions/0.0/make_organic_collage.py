#!/usr/bin/env python3
"""
make_organic_collage.py - Organische Collage mit maximaler Flächenausnutzung
Keine Hauptflächen mehr als MAX_OVERLAP_RATIO verdeckt, leichte Skalierung zum Füllen
"""
import os
import random
import argparse
from PIL import Image

MAX_OVERLAP_RATIO = 0.3  # Maximaler Anteil der Hauptfläche, der überdeckt werden darf
MAX_ITER = 1000           # Max Versuche pro Bild

def parse_color(c):
    c = str(c).strip()
    if c.startswith("#"):
        c = c.lstrip("#")
        if len(c) == 3:
            c = ''.join([ch*2 for ch in c])
        return tuple(int(c[i:i+2], 16) for i in (0,2,4))
    if "," in c:
        parts = [int(x.strip()) for x in c.split(",")]
        return tuple(parts[:3])
    raise ValueError("Ungültige Farbe. Nutze '#RRGGBB' oder 'R,G,B'.")

def rect_overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0
    return (ix2 - ix1) * (iy2 - iy1)

def inner_box(cx, cy, w, h, protected_frac):
    iw = w * protected_frac
    ih = h * protected_frac
    return (cx - iw/2, cy - ih/2, cx + iw/2, cy + ih/2)

def load_images(input_dir, style_settings):
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))])
    if not files:
        raise SystemExit("Keine Bilddateien gefunden.")
    items = []
    for f in files:
        try:
            pil = Image.open(os.path.join(input_dir, f)).convert("RGBA")
            iw, ih = pil.size
            scale = random.uniform(style_settings["scale_min"], style_settings["scale_max"])
            sw = max(12, int(iw*scale))
            sh = max(12, int(ih*scale))
            pil = pil.resize((sw, sh), Image.LANCZOS)
            items.append({"name": f, "img": pil, "w": sw, "h": sh})
        except:
            print("Warnung: konnte", f, "nicht laden")
    # Große Bilder zuerst
    items.sort(key=lambda x: x["w"]*x["h"], reverse=True)
    return items

def place_images(items, canvas_w, canvas_h, protected_frac, max_rotation):
    placed = []
    for it in items:
        for _ in range(MAX_ITER):
            # Leicht zufällige Position
            cx = random.uniform(it["w"]/2, canvas_w - it["w"]/2)
            cy = random.uniform(it["h"]/2, canvas_h - it["h"]/2)
            angle = random.uniform(-max_rotation, max_rotation)
            rot_img = it["img"].rotate(angle, expand=True, resample=Image.BICUBIC)
            rot_w, rot_h = rot_img.size
            main_box = inner_box(cx, cy, rot_w, rot_h, protected_frac)
            # Überlappung prüfen
            max_ratio = 0
            for p in placed:
                other_box = inner_box(p["cx"], p["cy"], p["rot_w"], p["rot_h"], protected_frac)
                overlap_area = rect_overlap(main_box, other_box)
                main_area = (main_box[2]-main_box[0])*(main_box[3]-main_box[1])
                ratio = overlap_area/main_area if main_area>0 else 0
                max_ratio = max(max_ratio, ratio)
            if max_ratio <= MAX_OVERLAP_RATIO:
                it.update({"cx": cx, "cy": cy, "rot_img": rot_img, "rot_w": rot_w, "rot_h": rot_h, "angle": angle})
                placed.append(it)
                break
        else:
            # Wenn MAX_ITER erreicht, minimal skalieren und trotzdem platzieren
            scale_factor = 0.95
            new_w = int(it["w"]*scale_factor)
            new_h = int(it["h"]*scale_factor)
            it["rot_img"] = it["img"].resize((new_w,new_h), Image.LANCZOS).rotate(angle, expand=True)
            it.update({"cx": cx, "cy": cy, "rot_w": new_w, "rot_h": new_h, "angle": angle})
            placed.append(it)
    return placed

def create_collage(input_dir, width, height, bgcolor, style, max_rotation, protected_frac, overlap_factor, output):
    style_presets = {
        "simple": {"scale_min":0.85, "scale_max":0.95},
        "organic": {"scale_min":0.9, "scale_max":1.05},
        "chaotic": {"scale_min":0.75, "scale_max":1.2},
    }
    s = style_presets.get(style, style_presets["organic"])
    items = load_images(input_dir, s)
    placed = place_images(items, width, height, protected_frac, max_rotation)

    # Zweiter Durchlauf: kleine Lücken füllen
    for it in placed:
        cx, cy = it["cx"], it["cy"]
        img = it["rot_img"]
        w, h = img.size
        # leicht skalieren, nur wenn keine Hauptfläche überdeckt
        scale_steps = [1.02,1.05,1.08]
        for scale in scale_steps:
            new_w = int(w*scale)
            new_h = int(h*scale)
            scaled_img = it["img"].resize((new_w,new_h), Image.LANCZOS).rotate(it["angle"], expand=True)
            main_box = inner_box(cx, cy, new_w, new_h, protected_frac)
            overlap_ok = True
            for p in placed:
                if p==it: continue
                other_box = inner_box(p["cx"], p["cy"], p["rot_w"], p["rot_h"], protected_frac)
                overlap_area = rect_overlap(main_box, other_box)
                main_area = (main_box[2]-main_box[0])*(main_box[3]-main_box[1])
                ratio = overlap_area/main_area if main_area>0 else 0
                if ratio > MAX_OVERLAP_RATIO:
                    overlap_ok = False
                    break
            if overlap_ok:
                it["rot_img"] = scaled_img
                it["rot_w"], it["rot_h"] = scaled_img.size

    canvas = Image.new("RGB", (width, height), bgcolor)
    for it in placed:
        img = it["rot_img"]
        px = int(it["cx"] - it["rot_w"]/2)
        py = int(it["cy"] - it["rot_h"]/2)
        canvas.paste(img, (px, py), img)
    canvas.save(output)
    print("Saved collage:", output)

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Ordner mit Bildern")
    p.add_argument("--width", type=int, default=2560)
    p.add_argument("--height", type=int, default=1440)
    p.add_argument("--bgcolor", default="#222222", help="Hintergrundfarbe '#rrggbb' oder 'r,g,b'")
    p.add_argument("--style", choices=["simple","organic","chaotic"], default="organic")
    p.add_argument("--max-rotation", type=float, default=5.0)
    p.add_argument("--protected", type=float, default=0.7)
    p.add_argument("--overlap-factor", type=float, default=1.0)
    p.add_argument("--output", default="collage.png")
    args = p.parse_args()
    bgcolor_rgb = parse_color(args.bgcolor)
    create_collage(args.input, args.width, args.height, bgcolor_rgb, args.style, args.max_rotation, args.protected, args.overlap_factor, args.output)
