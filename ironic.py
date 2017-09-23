from PIL import Image
import math
from collections import OrderedDict
import json

defaultc = 10

class JsonMap:
    def __init__(self, mapname="", background_color="#000000", length=9999, width=9999, theme='overworld', entry=(0,64)):
        self.dict = OrderedDict()
        self.create_empty()
        self.set_map_name(mapname)
        self.set_background_color(background_color)
        self.set_width(length)
        self.set_height(width)
        self.set_theme(theme)

    def set_width(self, length):
        self.dict['background'][1] = length

    def set_height(self, width):
        self.dict['background'][2] = width

    def set_theme(self, theme):
        self.dict['theme'] = theme


    def set_background_color(self, str):
        assert str.startswith("#")

        self.dict['background'][0] = str

    def set_map_name(self, str):
        self.dict['MapName'] = str


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
        self.dict['MapName'] = ''
        self.dict['blocks'] = OrderedDict()
        self.dict['entities'] = OrderedDict()
        self.dict['background'] = [None, None, None]
        self.dict['default_entry'] = [0, 64]

    def sort(self):
        for item in self.dict['blocks'].values():
            item.sort()

        for item in self.dict['entities'].values():
            item.sort()

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
IMAGE_EPSILON = 1


def save(img, name='out.png'):
    img.save(name)

class TextureStore:
    def __init__(self, searchitems, pipe):
        self.pipe = list(pipe)
        self.rawsearch = searchitems

    def searchitems(self):
        return self.rawsearch.items()


class ImageCrop:

    aboveitems = TextureStore({
        'brick' : Image.open(join('above', "brick.png")).histogram(),
        'metal': Image.open(join('above', "metal.png")).histogram(),
        'pipe': Image.open(join('above', "pipe.png")).histogram(),

        'brickCoin': Image.open(join('above', 'brickcoin.png')).histogram(),
        'brickMushroom' : Image.open(join('above', 'brickmushroom.png')).histogram(),

        'goomba': Image.open(join('above', 'goomba.png')).histogram(),
        'ground': Image.open(join("above", "ground.png")).histogram(),

        'questionMushroom': Image.open(join('above', "questionmushroom.png")).histogram(),
        'questionCoin': Image.open(join('above', 'questioncoin.png')).histogram(),

        'invisCoin' : Image.open(join('above', 'inviscoin.png')).histogram(),
        'invis1up' : Image.open(join('above', 'invis1up.png')).histogram(),

        'cloud' : Image.open(join('above', 'cloud.png'))
    },
    [Image.open(join('above', 'pipe1.png')).histogram(),
     Image.open(join('above', 'pipe2.png')).histogram(),
     Image.open(join('above', 'pipe3.png')).histogram(),
     Image.open(join('above', 'pipe4.png')).histogram()
     ])
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
        return self.map.crop((self.startx + x*BLOCK_SIZE,
                              self.starty - (y+1)*BLOCK_SIZE,
                              self.startx + (x+1)*BLOCK_SIZE,
                              self.starty - y*BLOCK_SIZE))



    def __init__(self, startx, starty, fp, search_items, json=None, background_color="#000000", map_name=""):
        self.json = json if json is not None else JsonMap()
        self.fp = fp
        self.startx = startx
        self.starty = starty
        self.map = Image.open(fp)


        self.width =self.map.width
        self.height = self.map.height

        self.width_blocks = (self.width - startx) // BLOCK_SIZE
        self.height_blocks = (starty) // BLOCK_SIZE

        self.search_items = search_items

        if search_items == self.aboveitems:
            self.theme = 'overworld'
        elif search_items == self.belowitems:
            self.theme = 'underground'
        else:
            raise Exception()

        self.json.set_theme(self.theme)
        self.json.set_background_color(background_color)
        self.json.set_width(self.width_blocks*GBLOCK_SIZE)
        self.json.set_height(self.height_blocks*GBLOCK_SIZE)
        self.json.set_map_name(map_name)

        self.todo_items = {(x,y) for x in range(self.width_blocks) for y in range(self.height_blocks)}



    def bfs_pipe(self, x, y):

        return self.bfs(x, y, self.search_items.pipe)

    def bfs(self, x, y, list_of_histogram):
        # can be image or list of images


        assert isinstance(list_of_histogram, (tuple, list))

        min_x = x
        max_x = x
        min_y = y
        max_y = y
        stack = [(x,y)]
        done = {(x,y)}

        del x, y # clean up these parameters so i dont accidently use them


        while stack:
            current = stack.pop()
            for xy in self.get_points(*current):
                current_image = self.get_image(*xy)
                if xy not in done and self.match(current_image, list_of_histogram):
                    if xy in self.todo_items:
                        self.todo_items.remove(xy)
                    done.add(xy)
                    stack.append(xy)
                    min_x = min(min_x, xy[0])
                    max_x = max(max_x, xy[0])
                    min_y = min(min_y, xy[1])
                    max_y = max(max_y, xy[1])

        return min_x, min_y, max_x - min_x+1, max_y - min_y+1
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
        return [e for e in ((i[0]+point[0], i[1]+point[1]) for i in self.offsets) if self.in_grid(*e)]

    def in_grid(self, x, y):
        if x < 0 or x >= self.width_blocks:
            return False
        if y < 0 or y >= self.width_blocks:
            return False
        return True
        # uses >= cuz it is 0 indexed


    def bfs_ground(self, x, y):
        return self.bfs(x, y, [self.search_items.rawsearch['ground']])

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
        print(self.todo_items)


        while self.todo_items:
            x,y = self.todo_items.pop()
            img = self.get_image(x,y)
            hist = img.histogram()


            for name, comp_img in self.search_items.searchitems():
                if self.is_close(hist ,comp_img):
                    if name == 'brick':
                        self.json.add_block('blockBreakableBrick', x, y)

                    elif name == 'metal':
                        self.json.add_block('blockMetal', x, y)

                    elif name == "pipe":
                        opts = self.bfs_pipe(x, y)
                        self.json.add_block('blockPipe', *opts, "none")


                    elif name == 'ground':
                        opts = self.bfs_ground(x, y)
                        self.json.add_block('groundPlatform', *opts)

                    elif name == 'questionMushroom':
                        self.json.add_block('blockQuestion', x, y, "DefaultFire")

                    elif name == 'questionCoin':
                        self.json.add_block('blockQuestion', x, y, 'Coin')

                    elif name == 'brickCoin':
                        self.json.add_block('blockBrickCoin', x, y)

                    elif name == 'invis1up':
                        self.json.add_block('blockInvis1up', x, y)

                    elif name == 'invisCoin':
                        self.json.add_block('blockInvisCoin', x, y)



                    elif name == 'goomba':
                        self.json.add_entity('entGoomba', x, y)


                    elif name == 'koopa':
                        self.json.add_entity('entKoopa', x, y)


                    elif name == 'coin':
                        self.json.add_entity('entCoin', x, y)





                    else:
                        raise Exception("cant find " + str(name))


                    print("Found {} at x:{}, y{}".format(name,x, y))
                    break
            else:
                if DB:
                    input("cant find!")
                    save(img, "cantfind.png")

        self.json.sort()


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

DB = False
GBLOCK_SIZE = 32

def unittest():
    #test = ImageCrop(0, 240, join('maps', '1-1.png'), ImageCrop.aboveitems)

    test = ImageCrop(0, 240, join("maps", "1-3.png"), ImageCrop.aboveitems, background_color="#5c94fc",
                       map_name="2-1above")

    assert ImageCrop.is_close(test.get_image(0, 0), Image.open(join('tests', 'aboveground.png')))
    assert ImageCrop.is_close(test.get_image(1, 0), Image.open(join('tests', 'aboveground.png')))
    #assert ImageCrop.is_close(test.get_image(0, 2), Image.open(join('tests', '1.3.png')))
    save(test.get_image(80, 9), 'test.png')
    save(test.get_image(80, 10), 'test.png')
    save(test.get_image(81, 9), 'test.png')

    #test.search()
    print("passed unittests")
#y = JsonMap()
#y.add_block('b', 0, 0)
#print(y.dumps())
#ImageCrop.get_cord(Image.open("1-1.png"), 1,0, x, y)
#
# = top pixel before off ground for images
unittest()

level1 = ImageCrop(0, 240, join("maps","1-1.png"), ImageCrop.aboveitems, background_color="#5c94fc", map_name="1-1above")
level1.search()

#level1 = ImageCrop(0, 480, join("maps","2-1.png"), ImageCrop.aboveitems, background_color="#5c94fc", map_name="2-1above")
#level1.search()

#level1 = ImageCrop(0, 240, join("maps","1-3.png"), ImageCrop.aboveitems, background_color="#5c94fc", map_name="2-1above")
#level1.search()



#ImageCrop.get_cord(Image.open("maps/1-2.png"), 70 ,7, 0, 464)
with open('out.json', 'w') as f:
    f.write(level1.json.dumps())