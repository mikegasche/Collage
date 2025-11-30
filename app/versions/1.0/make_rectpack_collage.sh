#!/bin/sh


python3 make_rectpack_collage.py --input ./input --width 2560 --height 1440 --bgcolor transparent --output collage.png --max-rotation 1 --overlap-factor 0.05 --rows 2 --iterations 20

#python3 make_rectpack_collage.py --input . --width 2560 --height 1440 --output collage.png --max-rotation 5 --overlap-factor 0.05
#python3 make_rectpack_collage.py --input . --width 2560 --height 1440 --output collage.png --max-rotation 5 --overlap-factor 0.1
#python3 make_rectpack_collage.py --input . --width 2560 --height 1440 --output collage.png --max-rotation 0 --overlap-factor 0.1
