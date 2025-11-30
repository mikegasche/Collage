#!/usr/bin/env python3
# make_collage_grid.py
from PIL import Image
import os
import argparse
import math

def make_collage(input_folder, output_file="collage.png", canvas_width=2560, canvas_height=1080, padding=5, bg_color=(40,40,40)):
    images = [Image.open(os.path.join(input_folder, f)) for f in os.listdir(input_folder)
              if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("Keine Bilder gefunden!")
        return
    
    n = len(images)
    cols = math.ceil(math.sqrt(n * canvas_width / canvas_height))
    rows = math.ceil(n / cols)

    # Kachelgrößen berechnen
    thumb_width = (canvas_width - padding*(cols+1)) // cols
    thumb_height = (canvas_height - padding*(rows+1)) // rows

    new_im = Image.new('RGB', (canvas_width, canvas_height), bg_color)

    for idx, im in enumerate(images):
        col = idx % cols
        row = idx // cols

        # proportional skalieren
        im_ratio = im.width / im.height
        cell_ratio = thumb_width / thumb_height
        if im_ratio > cell_ratio:
            w = thumb_width
            h = int(thumb_width / im_ratio)
        else:
            h = thumb_height
            w = int(thumb_height * im_ratio)

        # zentrieren in Zelle
        x = padding + col * (thumb_width + padding) + (thumb_width - w)//2
        y = padding + row * (thumb_height + padding) + (thumb_height - h)//2

        im_resized = im.resize((w,h), Image.LANCZOS)
        new_im.paste(im_resized, (x,y))

    new_im.save(output_file)
    print(f"Collage gespeichert als {output_file}, Größe: {canvas_width}x{canvas_height}, Raster {cols}x{rows}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--width", type=int, default=2560)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--padding", type=int, default=5)
    parser.add_argument("--output", default="collage.png")
    args = parser.parse_args()

    make_collage(args.input, args.output, args.width, args.height, args.padding)
