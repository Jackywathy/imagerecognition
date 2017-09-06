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
            assert "already added" and False

        self.dict['blocks'].setdefault(block, []).append((args))

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

class ImageCrop:

    aboveitems = {
            'a_breakableBrickBlock' : Image.open(join('above', "brick.png")).histogram(),
            'a_blockMetal': Image.open(join('above', "metal.png")).histogram(),
            'a_blockPipe': Image.open(join('above', "pipe.png")).histogram(),

            'a_brickCoin': Image.open(join('above', 'brickcoin.png')).histogram(),

            'a_entGoomba': Image.open(join('above', 'goomba.png')).histogram(),


            'b_breakableBrickBlock': Image.open(join('below', "brick.png")).histogram(),
            'b_blockMetal': Image.open(join('below', 'metal.png')).histogram(),
            'b_blockBrickCoin': Image.open(join('below','brickcoin.png')).histogram(),
            'b_brickStar': Image.open(join('below', 'brickstar.png')).histogram(),
            'b_brickMushroom': Image.open(join('below', 'brickmushroom.png')).histogram(),



            'b_entCoin' : Image.open(join('below', 'coin.png')).histogram(),
            'b_entGoomba': Image.open(join('below', 'goomba.png')).histogram(),
            'b_entKoopa': Image.open(join('below', 'koopa.png')).histogram(),





            'blockQuestionMushroom': Image.open(join('above', "questionmushroom.png")).histogram(),
            'blockQuestionCoin' : Image.open(join('above', 'questioncoin.png')).histogram(),




        }



    def __init__(self, startx, starty, fp, json=None, type=aboveitems):
        self.json = json if json is not None else JsonMap()
        self.fp = fp
        self.type = type
        self.search(startx, starty, fp)


    def search(self, startx, starty, fp):
        # start x, start y is top left of first block
        # will travel right and up till hits the top
        img = Image.open(fp)
        for row in range((img.height-starty)//16):
            for col in range(img.width//16):

                x = startx+col*16
                y = starty-row*16
                #self.crop(img, x, y, histogram=False).save("me.png")
                #    pass
                for name, comp_img in self.type.items():

                    if self.rms(self.crop(img, x, y),comp_img) < 0.5:
                        realcol = col + 1 # real col as col is +1 in json in game
                        realrow = row + 1


                        if name == "a_blockPipe":
                            # stop if it is just touching the pipe undeneath
                            if self.json.is_block('a_blockPipe', realcol, realrow-1, 'none') or self.json.is_block('a_blockPipe', realcol, realrow-2, 'none'):
                                continue
                            else:
                                self.json.add_block('a_blockPipe', realcol, realrow, "none")

                        elif name == 'b_blockPipe':
                            if self.json.is_block('b_blockPipe', realcol, realrow - 1, 'none') or self.json.is_block(
                                    'b_blockPipe', realcol, realrow - 2, 'none'):
                                continue
                            else:
                                self.json.add_block('b_blockPipe', realcol, realrow, "none")


                        elif name == 'blockQuestionMushroom' :
                            self.json.add_block('blockQuestion', realcol, realrow, "DefaultFire")

                        elif name == 'blockQuestionCoin':
                            self.json.add_block('blockQuestion', realcol, realrow, 'Coin')

                        elif name == 'a_brickCoin':
                            self.json.add_block('a_blockBrickPowerUp', realcol, realrow, "coin", defaultc)

                        elif name == 'b_brickCoin':
                            self.json.add_block('b_blockBrickPowerUp', realcol, realrow, "coin", defaultc)

                        elif name == 'a_entGoomba':
                            self.json.add_entity('a_entGoomba', realcol, realrow)

                        elif name == 'b_entGoomba':
                            self.json.add_entity('b_entGoomba', realcol, realrow)

                        elif name == 'a_entKoopa':
                            self.json.add_entity('a_entKoopa', realcol, realrow)

                        elif name == 'b_entKoopa':
                            self.json.add_entity('b_entKoopa', realcol, realrow)

                        elif name == 'a_coin' or name == 'b_coin':
                            self.json.add_entity('entCoin', realcol, realrow)





                        else:
                            self.json.add_block(name, realcol, realrow)
                        print("Found {} at x:{}, y{}".format(name,realcol,realrow))


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



#y = JsonMap()
#y.add_block('b', 0, 0)
#print(y.dumps())
#ImageCrop.get_cord(Image.open("1-1.png"), 1,0, x, y)
#
# = top pixel before off ground for images

level1 = ImageCrop(0, 224, "maps/1-1.png")
#level2 = ImageCrop(0, 464, "maps/1-2.png")


#ImageCrop.get_cord(Image.open("maps/1-2.png"), 70 ,7, 0, 464)
#with open('out.json', 'w') as f:
#    f.write(z.json.dumps())