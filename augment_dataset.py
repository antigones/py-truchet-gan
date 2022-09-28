import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageOps
import truchet

import numpy as np
import random as rd

def main():
    
    n_samples = 1000
    how_many_tiles = 4
    of_size = 8
    img_mode = "L"
    
    tiles_representations = []
    for i in range(int(n_samples)):
        truchet_pattern = truchet.TruchetPattern(how_many_tiles, of_size, 'white', 'black','simple')
        img = truchet_pattern.paint_a_truchet()
        if img.mode != img_mode:
            img = img.convert(img_mode)
        tiles_representations.append(truchet_pattern.rand_succession)
        imageio.imsave("imgs/train/"+str(i)+".gif", img)

    print('*** DATASET CARDINALITY ***')
    print(n_samples)
    print('*** SET CARDINALITY ***')
    
    keys = []
    for elem in tiles_representations:
        if elem not in keys:
            keys.append(elem)
    print(len(keys))
    # print(keys)
if __name__ == '__main__':
    main()

