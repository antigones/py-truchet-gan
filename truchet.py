
from PIL import Image, ImageDraw
import random as rd
import imageio

class TruchetPattern:

    def __init__(self, how_many_tiles:int, tile_size:int, bg_color: str, fg_color:str, kind:str):
        self.how_many_tiles = how_many_tiles
        self.tile_size = tile_size
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.kind = kind

    def create_simple_tile(self) -> Image:
        tile_img = Image.new("RGB", (self.tile_size, self.tile_size))
        tile_img_draw = ImageDraw.Draw(tile_img)
        tile_img_draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill = self.bg_color)
        tile_img_draw.polygon([(0, 0), (self.tile_size, 0), (0, self.tile_size)], fill = self.fg_color )
        return tile_img
        
    def create_smith_tile(self, ) -> Image:
        tile_img = Image.new("RGB", (self.tile_size, self.tile_size))
        tile_img_draw = ImageDraw.Draw(tile_img)
        tile_img_draw.rectangle([(0, 0), (self.tile_size, self.tile_size)], fill = self.bg_color)
        tile_img_draw.arc([(-self.tile_size//2,-self.tile_size//2), (self.tile_size//2, self.tile_size//2)],0,-270,fill = self.fg_color)
        tile_img_draw.arc([(self.tile_size//2,self.tile_size//2), (self.tile_size +(self.tile_size//2), self.tile_size+(self.tile_size//2))],0,360,fill = self.fg_color)
        return tile_img

    def create_base_tile(self) -> Image:
        if self.kind == 'simple':
            tile_img = self.create_simple_tile()
        elif self.kind == 'smith':
            tile_img = self.create_smith_tile()
        else:
            raise Exception("Sorry, this tiling kind does not exists")
        imageio.imsave("base_tile.gif", tile_img)
        return tile_img

    def paint_a_truchet(self) -> Image:
        base_tile = self.create_base_tile()
        w, h = self.how_many_tiles * self.tile_size, self.how_many_tiles * self.tile_size
        img = Image.new("RGB", (w, h))
        for i in range(self.how_many_tiles):
            for j in range(self.how_many_tiles):
                offset = (i * self.tile_size, j * self.tile_size)
                # toss for rotation
                r = rd.randint(0,3)
                base_tile = base_tile.rotate(90 * r)
                img.paste(base_tile, offset)
        return img
