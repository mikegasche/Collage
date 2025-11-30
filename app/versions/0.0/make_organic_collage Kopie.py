#!/usr/bin/env python3
"""
make_organic_collage.py - intelligente Collage mit Hauptflächen-Schutz
Benötigt: Pillow (PIL)
"""
import os
import math
import random
import argparse
from PIL import Image

# -------------------------
# Hilfsfunktionen
# -------------------------
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

def inner_box_of(rot_w, rot_h, cx, cy, protected_frac):
    iw = rot_w * protected_frac
    ih = rot_h * protected_frac
    return (cx - iw/2, cy - ih/2, cx + iw/2, cy + ih/2)

def rect_overlap_area(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0
    return (ix2 - ix1) * (iy2 - iy1)

# -------------------------
# Collage-Funktion
# -------------------------
def create_collage(input_dir, width, height, bgcolor, style, max_angle, protected_frac, overlap_factor, output):
    files = [f for f in sorted(os.listdir(input_dir)) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
    if not files:
        raise SystemExit("Keine Bilddateien im Ordner gefunden.")
    imgs = []
    for f in files:
        try:
            imgs.append((f, Image.open(os.path.join(input_dir, f)).convert("RGBA")))
        except Exception as e:
            print("Warnung: konnte", f, "nicht öffnen:", e)

    n = len(imgs)

    # Style-Presets
    style_settings = {
        "simple":  {"scale_min":0.75, "scale_max":0.95, "angle_factor":0.5, "jitter":0.05},
        "organic": {"scale_min":0.85, "scale_max":1.05, "angle_factor":1.0, "jitter":0.08},
        "chaotic": {"scale_min":0.65, "scale_max":1.25, "angle_factor":1.5, "jitter":0.15}
    }
    s = style_settings.get(style, style_settings["organic"])
    s["overlap_factor"] = overlap_factor

    # Adaptive Skalierung: Berechne durchschnittliche Fläche pro Bild
    target_area = (width * height) / n

    # Bilder vorbereiten
    items = []
    for fname, pil in imgs:
        iw, ih = pil.size
        scale_factor = math.sqrt(target_area / (iw*ih)) * random.uniform(s["scale_min"], s["scale_max"])
        sw = max(12, int(iw*scale_factor))
        sh = max(12, int(ih*scale_factor))
        pil_scaled = pil.resize((sw, sh), Image.LANCZOS)
        items.append({"name": fname, "img": pil_scaled, "w": sw, "h": sh})

    # Sortiere absteigend nach Fläche: große Bilder zuerst
    items.sort(key=lambda it: it["w"]*it["h"], reverse=True)

    # Platzierung der Bilder
    placed = []
    for it in items:
        best_pos = None
        best_free = -1
        # Versuche mehrere zufällige Positionen
        for attempt in range(200):
            cx = random.uniform(it["w"]/2, width - it["w"]/2)
            cy = random.uniform(it["h"]/2, height - it["h"]/2)
            # Random Rotation
            angle = random.uniform(-max_angle*s["angle_factor"], max_angle*s["angle_factor"])
            rot_img = it["img"].rotate(angle, expand=True, resample=Image.BICUBIC)
            rot_w, rot_h = rot_img.size
            # Berechne Hauptfläche
            main_box = inner_box_of(rot_w, rot_h, cx, cy, protected_frac)
            # Prüfe Hauptflächen-Kollisionen
            min_overlap = 0
            for p in placed:
                other_box = inner_box_of(p["rot_w"], p["rot_h"], p["cx"], p["cy"], protected_frac)
                min_overlap = max(min_overlap, rect_overlap_area(main_box, other_box))
            # Wähle Position mit minimaler Überdeckung
            if min_overlap == 0:
                best_pos = (cx, cy, rot_img, rot_w, rot_h, angle)
                break
            elif min_overlap < best_free or best_free == -1:
                best_free = min_overlap
                best_pos = (cx, cy, rot_img, rot_w, rot_h, angle)
        if best_pos is None:
            # Fallback: zufällig platzieren
            best_pos = (cx, cy, rot_img, rot_w, rot_h, angle)
        # Speichern
        cx, cy, rot_img, rot_w, rot_h, angle = best_pos
        it.update({"cx": cx, "cy": cy, "rot_img": rot_img, "rot_w": rot_w, "rot_h": rot_h, "angle": angle})
        placed.append(it)

    # Canvas erstellen
    canvas = Image.new("RGB", (width, height), bgcolor)
    for it in placed:
        img = it["rot_img"]
        px = int(it["cx"] - it["rot_w"]/2)
        py = int(it["cy"] - it["rot_h"]/2)
        canvas.paste(img, (px, py), img)

    canvas.save(output)
    print("Saved collage:", output)

# -------------------------
# CLI
# -------------------------
if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Ordner mit Bildern")
    p.add_argument("--width", type=int, default=2560)
    p.add_argument("--height", type=int, default=1440)
    p.add_argument("--bgcolor", default="#222222", help="Hintergrundfarbe '#rrggbb' oder 'r,g,b'")
    p.add_argument("--style", choices=["simple", "organic", "chaotic"], default="organic")
    p.add_argument("--max-rotation", type=float, default=5.0, help="Max Rotationswinkel in Grad")
    p.add_argument("--protected", type=float, default=0.70, help="geschützte zentrale Fläche (0..1)")
    p.add_argument("--overlap-factor", type=float, default=1.0, help="Feinsteuerung Überlappung, multipliziert mit Style-Faktor")
    p.add_argument("--output", default="collage.png")
    args = p.parse_args()

    bgcolor_rgb = parse_color(args.bgcolor)
    create_collage(args.input, args.width, args.height, bgcolor_rgb, args.style, args.max_rotation, args.protected, args.overlap_factor, args.output)
