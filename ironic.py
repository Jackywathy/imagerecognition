from PIL import Image
import math
from collections import OrderedDict
import json

defaultc = 10

class JsonMap:
    def __init__(self):
        self.dict = OrderedDict()
        self.create_empty()



    def set_background_color(self, str):
        assert str.startswith("#")

        self.dict['background'][0] = str

    def set_map_name(self, str):
        self.dict['map_name'] = str


    def add_block(self, block, *args):

        if block in self.dict['blocks'] and args in self.dict['blocks'][block]:
            print(self.dumps())
            assert "already added" and False

        self.dict['blocks'].setdefault(block, []).append(args)

    def is_block(self, block, *args):
        if block not in self.dict['blocks']:
            return False

        return args in self.dict['blocks'][block]

    def add_entity(self, ent, *args):
        self.dict['entities'].setdefault(ent, []).append((args))




    def create_empty(self):
        self.dict['map_name'] = ''
        self.dict['blocks'] = OrderedDict()
        self.dict['entities'] = OrderedDict()
        self.dict['background'] = []
        self.dict['background_music'] = ''
        self.dict['default_entry'] = [0, 64]

    def dumps(self):
        return json.dumps(self.dict, indent=4)


from os.path import join
ground_literal = "groundPlatform"


above = 0
below = 1

brick = 0
metal = 1
pipe = 2
brickCoin = 3
goomba = 4
ground = 5

BLOCK_SIZE = 16
IMAGE_EPSILON = 0.5


def save(img, name='out.png'):
    img.save(name)

class ImageCrop:

    aboveitems = {
        'brick' : Image.open(join('above', "brick.png")).histogram(),
        'metal': Image.open(join('above', "metal.png")).histogram(),
        'pipe': Image.open(join('above', "pipe.png")).histogram(),

        'brickCoin': Image.open(join('above', 'brickcoin.png')).histogram(),

        'goomba': Image.open(join('above', 'goomba.png')).histogram(),
        'ground': Image.open(join("above", "ground.png")).histogram(),

        'questionMushroom': Image.open(join('above', "questionmushroom.png")).histogram(),
        'questionCoin': Image.open(join('above', 'questioncoin.png')).histogram(),
    }
    belowitems = {
        'brick': Image.open(join('below', "brick.png")).histogram(),
        'metal': Image.open(join('below', 'metal.png')).histogram(),
        'pipe' : Image.open(join('below', 'pipe.png')).histogram(),

        'brickCoin': Image.open(join('below','brickcoin.png')).histogram(),

        'brickStar': Image.open(join('below', 'brickstar.png')).histogram(),
        'brickMushroom': Image.open(join('below', 'brickmushroom.png')).histogram(),


        'coin' : Image.open(join('below', 'coin.png')).histogram(),
        'goomba': Image.open(join('below', 'goomba.png')).histogram(),
        'koopa': Image.open(join('below', 'koopa.png')).histogram(),

        }

    def get_image(self, x, y):
        return self.map.crop((self.startx + (x-1)*BLOCK_SIZE,
                              self.starty - y*BLOCK_SIZE,
                              self.startx + x*BLOCK_SIZE,
                              self.starty - (y-1)*BLOCK_SIZE))

    def __init__(self, startx, starty, fp, search_items, json=None):
        self.json = json if json is not None else JsonMap()
        self.fp = fp
        self.startx = startx
        self.starty = starty
        self.map = Image.open(fp)


        self.width =self.map.width
        self.height = self.map.height

        self.width_blocks = (self.width - startx) // BLOCK_SIZE
        self.height_blocks = (self.height - starty) // BLOCK_SIZE

        self.search_items = search_items

        if search_items == self.aboveitems:
            self.theme = 'overworld'
        elif search_items == self.belowitems:
            self.theme = 'underground'
        else:
            raise Exception()

        self.todo_items = {(x,y) for x in range(1, self.map.width//BLOCK_SIZE+1) for y in range(1, (self.map.height-starty)//16)}

        self.search()


    def bfs_pipe(self, x, y):
        self.bfs(x, y, [self.search_items['pipe']])

    def bfs(self, x, y, list_of_histogram):
        # can be image or list of images


        assert isinstance(list_of_histogram, (tuple, list))

        min_x = x
        max_x = x
        min_y = y
        max_y = y
        stack = [(x,y)]
        del x, y # clean up these parameters so i dont accidently use them

        while stack:
            current = stack.pop()
            for xy in self.get_points(*current):
                current_image = self.get_image(*xy)
                if self.match(current_image, list_of_histogram):
                    self.todo_items.remove(xy)
                    stack.append(xy)
                    min_x = min(min_x, xy[0])
                    max_x = max(max_x, xy[0])
                    min_y = min(min_y, xy[1])
                    max_y = max(max_y, xy[1])

        return min_x, min_y, max_x - min_x, max_y - min_y
        # returns a rect Tuple of bottomleft, with width and height


    def match(self, img, list):
        return any((self.is_close(img, match) for match in list))




    @staticmethod
    def is_close(img1, img2):
        hist1 = img1.histogram() if isinstance(img1, Image.Image) else img1
        hist2 = img2.histogram() if isinstance(img2, Image.Image) else img2
        return ImageCrop.rms(hist1, hist2) < IMAGE_EPSILON





    offsets = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]
    def get_points(self, x,y):
        point = (x,y)
        return [e for e in ((i[0]+point[0], i[1]+point[1]) for i in self.offsets) if self.in_grid(*e) and e in self.todo_items]

    def in_grid(self, x, y):
        if x < 1 or x > self.width_blocks:
            return False
        if y < 1 or y > self.width_blocks:
            return False
        return True
        # uses > cuz it is 1 indexed



    """
    'brick' : Image.open(join('above', "brick.png")).histogram(),
    'metal': Image.open(join('above', "metal.png")).histogram(),
    'pipe': Image.open(join('above', "pipe.png")).histogram(),

    'brickCoin': Image.open(join('above', 'brickcoin.png')).histogram(),

    'goomba': Image.open(join('above', 'goomba.png')).histogram(),
    'ground': Image.open(join("above", "ground.png")).histogram(),

    'questionMushroom': Image.open(join('above', "questionmushroom.png")).histogram(),
    'questionCoin': Image.open(join('above', 'questioncoin.png')).histogram(),
    """

    def search(self):
        # start x, start y is top left of first block
        # will travel right and up till hits the top

        while self.todo_items:
            x,y = self.todo_items.pop()
            img = self.get_image(x,y)
            hist = img.histogram()

            for name, comp_img in self.search_items.items():
                if self.rms(hist ,comp_img) < 0.5:
                    if name == "pipe":
                        self.bfs_pipe(x, y)

                    elif name == 'questionMushroom':
                        self.json.add_block('blockQuestion', x, y, "DefaultFire")

                    elif name == 'questionCoin':
                        self.json.add_block('blockQuestion', x, y, 'Coin')

                    elif name == 'brickCoin':
                        self.json.add_block('blockBrickCoin', x, y)

                    elif name == 'goomba':
                        self.json.add_entity('EntGoomba', x, y)


                    elif name == 'koopa':
                        self.json.add_entity('EntKoopa', x, y)


                    elif name == 'coin':
                        self.json.add_entity('entCoin', x, y)


                    print("Found {} at x:{}, y{}".format(name,x, y))


    @staticmethod
    def rms(h1, h2):
        return math.sqrt(sum( map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))

    @staticmethod
    def crop(img, x, y, width=16, height=16, histogram=True):
        return img.crop((x,y,x+width,y+height)).histogram() if histogram else img.crop((x,y,x+width,y+height))


    @staticmethod
    def get_cord(img, x, y, startx, starty, name='out.png'):
        x = startx + (x-1) * 16
        y = starty - (y-1) * 16
        ImageCrop.crop(img, x, y, histogram=False).save(name)


def unittest():
    test = ImageCrop(0, 240, join('maps', '1-1.png'), ImageCrop.aboveitems)
    assert test.get_image(1,1) == Image.open(join('tests', 'aboveground.png'))
    assert test.get_image(1,2) == Image.open(join('tests', 'aboveground.png'))
    assert test.get_image(1, 3) == Image.open(join('tests', '1.3.png'))
    print("passed unittests")
#y = JsonMap()
#y.add_block('b', 0, 0)
#print(y.dumps())
#ImageCrop.get_cord(Image.open("1-1.png"), 1,0, x, y)
#
# = top pixel before off ground for images
unittest()
level1 = ImageCrop(0, 240, "maps/1-1.png", ImageCrop.aboveitems)
#print(level1.json.dumps())
#level2 = ImageCrop(0, 464, "maps/1-2.png")


#ImageCrop.get_cord(Image.open("maps/1-2.png"), 70 ,7, 0, 464)
with open('out.json', 'w') as f:
    f.write(level1.json.dumps())