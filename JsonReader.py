from collections import OrderedDict
import json


class JsonMap:
    """Json Representation of a marioMap"""
    def __init__(self, mapname="", background_color="#000000", length=9999, width=9999, theme='overworld', entry=(0,64)):
        self.dict = OrderedDict()
        self.create_empty()
        self.set_map_name(mapname)
        self.set_background_color(background_color)
        self.set_width(length)
        self.set_height(width)
        self.set_theme(theme)

    def set_width(self, length):
        self.dict['width'] = length

    def set_height(self, width):
        self.dict['height'] = width

    def set_theme(self, theme):
        self.dict['theme'] = theme


    def set_background_color(self, str):
        assert str.startswith("#")

        self.dict['BackgroundColor'] = str

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
        self.dict['BackgroundColor'] = None
        self.dict['DefaultEntry'] = [0, 64]
        self.dict['width'] = None
        self.dict['height'] = None
        self.dict['MapTime'] = 300
        self.dict['NextLevel'] = 'None'
        self.dict['LinkedLevel'] = 'None'
        self.dict['OnDead'] = 'None'



    def sort(self):
        for item in self.dict['blocks'].values():
            item.sort()

        for item in self.dict['entities'].values():
            item.sort()

    def dumps(self):
        return json.dumps(self.dict, indent=4)