# Mike's Collage

Organische Collagen aus Bildern erstellen – optimierte Flächennutzung, minimale Überlappung, optionale Rotation und transparenter Hintergrund.

## Installation

1. Python 3.x (>=3.9) installieren  
2. Virtuelle Umgebung einrichten (empfohlen):  
   
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Abhängigkeiten installieren:  
   
   ```
   pip install pillow
   ```

## Nutzung:

```
python3 make_rectpack_collage.py --input INPUT_DIR --width WIDTH --height HEIGHT --output OUTPUT_FILE [OPTIONS]
```

### Parameter

- --input INPUT_DIR : Ordner mit Bildern (.jpg, .jpeg, .png)  
- --width WIDTH : Breite des Gesamtbildes  
- --height HEIGHT : Höhe des Gesamtbildes  
- --output OUTPUT_FILE : Name der Collage-Ausgabedatei (.png empfohlen)  

### Optionale Parameter

- --bgcolor BGCOLOR : Hintergrundfarbe (#RRGGBB, R,G,B) oder transparent  
- --rows N : Anzahl Reihen (0 = automatisch)  
- --overlap-factor F : Maximaler Verschiebungs-/Überlappungsfaktor (Standard: 0.05)  
- --max-rotation DEG : Maximaler Drehwinkel in Grad (Standard: 5)  
- --iterations N : Anzahl Layout-Varianten zur Optimierung (Standard: 15)  

## Tipps für optimale Ergebnisse

| Bildanzahl | Canvas    | Rows | Overlap   | Rotation | Iterationen | Bemerkung                                              |
| ---------- | --------- | ---- | --------- | -------- | ----------- | ------------------------------------------------------ |
| 6–8        | 2560x1440 | 2    | 0.05–0.08 | 0–5°     | 15–20       | Gleichmäßig obere & untere Reihe, minimale Überlappung |
| 9–12       | 2560x1440 | 3    | 0.05–0.08 | 0–5°     | 20–25       | 3 Reihen, Fläche wird gut genutzt                      |
| 12–20      | 2560x1440 | 3–4  | 0.05–0.1  | 0–5°     | 25–40       | Iterationen erhöhen für bessere Optimierung            |
| <6         | beliebig  | 1–2  | 0.03–0.05 | 0–5°     | 10–15       | Einzelne Reihe oder automatisch                        |

## Hinweise

- Rows = 0 → Script wählt automatisch die beste Anzahl Reihen  
- Overlap-Factor → kleine Werte = wenig Überlappung, große Werte = organischer, verspielter Look  
- Max-Rotation → kleine Winkel für sichtbare Bilder, größere Winkel für künstlerische Wirkung  
- Iterations → je mehr Iterationen, desto besser das Ergebnis, dauert aber länger  
- Bgcoulor transparent → Collage mit Alpha-Kanal, perfekt für Layering  

## Beispiel-Aufrufe

1. Standard-Collage mit 2 Reihen und leichtem Overlap:  
   
   ```
   python3 make_rectpack_collage.py --input ./bilder --width 2560 --height 1440 --output collage.png --rows 2 --overlap-factor 0.05 --max-rotation 5 --iterations 20
   ```

2. Automatisches Layout für beliebige Bildanzahl, transparenter Hintergrund:  
   
   ```
   python3 make_rectpack_collage.py --input ./bilder --width 2560 --height 1440 --output collage.png --bgcolor transparent --rows 0 --iterations 25
   ```

## Schema – Beispiel: 8 Bilder, 2 Reihen, minimale Überlappung:

Obere Reihe (Bilder 1–4):

```
+-------+  +-------+  +-------+  +-------+
| Img 1 |  | Img 2 |  | Img 3 |  | Img 4 |
+-------+  +-------+  +-------+  +-------+
```

Untere Reihe (Bilder 5–8):

```
+-------+  +-------+  +-------+  +-------+
| Img 5 |  | Img 6 |  | Img 7 |  | Img 8 |
+-------+  +-------+  +-------+  +-------+
```

**Hinweise zu Schema**:

- Leichte Verschiebungen innerhalb Overlap-Factor möglich  
- Rotation optional, kann auch 0° sein  
- Größe proportional skaliert, um Gesamtfläche optimal zu nutzen  
- Transparenter Hintergrund unterstützt Alpha-Kanal  

## Lizenz

Dieses Script ist frei verwendbar und kann beliebig angepasst werden.
