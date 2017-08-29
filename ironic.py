from PIL import Image
import math
from functools import reduce
import operator
from collections import OrderedDict
import json


x = 0
y = 208


class JsonMap:
    def __init__(self):
        self.dict = OrderedDict()
        self.create_empty()



    def set_background_color(self, str):
        assert str.startswith("#")

        self.dict['background'][0] = str

    def set_map_name(self, str):
        self.dict['map_name'] = str


    def add_block(self, block, x, y):
        if (x, y) in self.dict.values():
            print("already exists!")
            return
        if block == 'b' or block == 'brick':
            type = 'blockBreakableBrick'
        elif block == 'q' or block == 'question':
            type  = 'blockQuestion'
        else:
            raise NotImplementedError("cant find {}".format(block))
        self.dict['blocks'].setdefault(type, []).append((x,y))



    def create_empty(self):
        self.dict['map_name'] = ''
        self.dict['blocks'] = OrderedDict()
        self.dict['entities'] = OrderedDict()
        self.dict['background'] = []
        self.dict['background_music'] = ''
        self.dict['default_entry'] = [0, 64]

    def dumps(self):
        return json.dumps(self.dict, indent=4)





class ImageCrop:
    ground = Image.open("ground.png").histogram()
    brick = Image.open("brick.png").histogram()
    metal = Image.open("metal.png").histogram()
    pipe = Image.open("pipe.png").histogram()

    def __init__(self, startx, starty, fp, json=None):
        self.json = json if json is not None else JsonMap()
        self.fp = fp
        self.search(startx, starty, fp)


    def search(self, startx, starty, fp):
        # start x, start y is top left of first block
        # will travel right and up till hits the top
        img = Image.open(fp)
        row = 0
        for col in range(img.width//16):
            x = startx+col*16
            y = starty+row*16
            print("x:{}, y:{}, diff: {}".format(x,y,self.rms(self.crop(img, x, y), self.ground)))

    @staticmethod
    def rms(h1, h2):
        return math.sqrt(sum( map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))

    @staticmethod
    def crop(img, x, y, width=16, height=16, histogram=True):
        return img.crop((x,y,x+width,y+height)).histogram() if histogram else img.crop((x,y+width,y+height))





h1 = Image.open("ground.png").histogram()
h2 = Image.open("1-1.png")
h2 = h2.crop((x, y, x + 16, y + 16))
h2.save("hi.png")
h2 = h2.histogram()

rms = math.sqrt(reduce(operator.add,
                       map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
print(rms)


y = JsonMap()
y.add_block('b', 0, 0)
print(y.dumps())

z = ImageCrop(x, 208, "1-1.png")
