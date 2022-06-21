import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import truchet

import numpy as np
import random as rd

def main():
  
    n_samples = 1000
    how_many_tiles = 8
    of_size = 8
    img_mode = "L"

    # for i in range(int(n_samples*0.80)):
    for i in range(int(n_samples)):
        img = truchet.paint_a_truchet(how_many_tiles, of_size)
        if img.mode != img_mode:
            img = img.convert(img_mode)

        imageio.imsave("imgs/train/"+str(i)+".gif", img)

if __name__ == '__main__':
    main()

