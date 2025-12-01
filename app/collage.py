# ------------------------------------------------------------------------------
# Copyright (c) 2025 Michael Gasche
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------

# File:        collage.py
# Version:     1.1
# Author:      Michael Gasche
# Created:     2025-12
# Product:     Collage
# Description: Organic collage with row layout, optimized vertical scaling, and iterations


import os
import argparse
import random
from PIL import Image
import math

def parse_color(c):
    c = str(c).strip().lower()
    if c == "transparent":
        return "transparent"
    if c.startswith("#"):
        c = c.lstrip("#")
        if len(c) == 3:
            c = ''.join([ch*2 for ch in c])
        return tuple(int(c[i:i+2],16) for i in (0,2,4))
    if "," in c:
        parts = [int(x.strip()) for x in c.split(",")]
        return tuple(parts[:3])
    raise ValueError("Invalid color. Use ‘#RRGGBB’, ‘R,G,B’, or ‘transparent’.")

def load_images(input_dir):
    files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg",".jpeg",".png"))]
    items = []
    for f in files:
        img = Image.open(os.path.join(input_dir, f)).convert("RGBA")
        w,h = img.size
        items.append({"name": f, "img": img, "w": w, "h": h})
    return items

def compute_layout(items, canvas_width, canvas_height, rows, overlap_factor, iterations):
    n = len(items)
    if rows <= 0:
        # Automatic selection: try 1..n rows
        best_layout = None
        best_score = None
        for r in range(1, n+1):
            layout, score = try_layout(items, canvas_width, canvas_height, r, overlap_factor, iterations)
            if best_score is None or score < best_score:
                best_score = score
                best_layout = layout
        return best_layout
    else:
        layout, _ = try_layout(items, canvas_width, canvas_height, rows, overlap_factor, iterations)
        return layout

def try_layout(items, canvas_width, canvas_height, rows, overlap_factor, iterations):
    """
    Test layout with given number of rows iteratively and return best found layout and score
    """
    best_layout = None
    best_score = None  #  free area + overlap
    for it in range(iterations):
        layout = []
        shuffled = items.copy()
        random.shuffle(shuffled)
        per_row = math.ceil(len(shuffled)/rows)

        # Calculate provisional height per row proportional to number of images
        row_items = []
        row_heights = []
        for r in range(rows):
            start = r*per_row
            end = min((r+1)*per_row, len(shuffled))
            row = shuffled[start:end]
            if not row:
                continue
            row_items.append(row)
            row_heights.append(max(item["h"] for item in row))

        # Scaling to utilize canvas height
        total_row_heights = sum(row_heights)
        if total_row_heights == 0:
            continue
        scale_y = min(1.0, canvas_height / total_row_heights)
        y = 0
        for rh, row in zip(row_heights, row_items):
            # Scale width per image within the row proportionally to row height
            total_width = sum(item["w"] * (rh/item["h"]) for item in row)
            scale_x = min(1.0, canvas_width / total_width)
            scale = min(scale_x, scale_y)
            x = 0
            for item in row:
                w_scaled = int(item["w"] * (rh/item["h"]) * scale)
                h_scaled = int(rh * scale)
                # small shift within overlap factor
                shift_x = int((random.random()-0.5) * overlap_factor * w_scaled)
                shift_y = int((random.random()-0.5) * overlap_factor * h_scaled)
                new_x = min(max(x + shift_x, 0), canvas_width - w_scaled)
                new_y = min(max(y + shift_y, 0), canvas_height - h_scaled)
                layout.append({"img": item["img"], "x": new_x, "y": new_y, "w": w_scaled, "h": h_scaled})
                x += w_scaled
            y += int(rh * scale)

        # Score: free area + overlap between rows
        used_area = sum(l["w"]*l["h"] for l in layout)
        free_area = canvas_width*canvas_height - used_area
        score = free_area
        if best_score is None or score < best_score:
            best_score = score
            best_layout = layout
    return best_layout, best_score

def create_collage(input_dir, width, height, bgcolor, output, max_rotation=5, overlap_factor=0.05, rows=0, iterations=15):
    items = load_images(input_dir)

    if not items:
        return None
    
    layout = compute_layout(items, width, height, rows, overlap_factor, iterations)

    if bgcolor == "transparent":
        canvas = Image.new("RGBA", (width, height), (0,0,0,0))
    else:
        canvas = Image.new("RGB", (width, height), bgcolor)

    for l in layout:
        img = l["img"].resize((l["w"], l["h"]), Image.LANCZOS)

        # optional rotation
        if max_rotation != 0:
            angle = random.uniform(-max_rotation, max_rotation)
            img = img.rotate(angle, expand=True)
            w_rot, h_rot = img.size
            new_x = min(max(l["x"], 0), width - w_rot)
            new_y = min(max(l["y"], 0), height - h_rot)
        else:
            new_x = l["x"]
            new_y = l["y"]

        canvas.paste(img, (new_x, new_y), img)

    canvas.save(output)
    print(f"Collage saved: {output}")
    
    return output

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Folder with images")
    parser.add_argument("--width", type=int, default=2560)
    parser.add_argument("--height", type=int, default=1440)
    parser.add_argument("--bgcolor", default="#222222")
    parser.add_argument("--output", default="collage.png")
    parser.add_argument("--max-rotation", type=float, default=5)
    parser.add_argument("--overlap-factor", type=float, default=0.05)
    parser.add_argument("--rows", type=int, default=0, help="0=automatic, >0=number of rows")
    parser.add_argument("--iterations", type=int, default=15, help="Iterations for layout optimization")
    args = parser.parse_args()

    bgcolor_rgb = parse_color(args.bgcolor)
    create_collage(
        args.input,
        args.width,
        args.height,
        bgcolor_rgb,
        args.output,
        max_rotation=args.max_rotation,
        overlap_factor=args.overlap_factor,
        rows=args.rows,
        iterations=args.iterations
    )
