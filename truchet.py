
from PIL import Image, ImageDraw
import random as rd

def create_base_tile(size: int, bg_color:str, fg_color: str) -> Image:
    tile_img = Image.new("RGB", (size, size))
    tile_img_draw = ImageDraw.Draw(tile_img)
    tile_img_draw.rectangle([(0, 0), (size, size)], fill = bg_color)
    tile_img_draw.polygon([(0, 0), (size, 0), (0, size)], fill = fg_color )
    return tile_img

def paint_a_truchet(how_many_tiles: int, tile_size: int) -> Image:
    base_tile = create_base_tile(tile_size, 'white', 'black')
   
    w, h = how_many_tiles * tile_size, how_many_tiles * tile_size
    
    img = Image.new("RGB", (w, h))
    for i in range(how_many_tiles):
        for j in range(how_many_tiles):
            offset = (i * tile_size, j * tile_size)
            # toss for rotation
            base_tile = base_tile.rotate(90 * rd.randint(0,3))
            img.paste(base_tile, offset)
    return img