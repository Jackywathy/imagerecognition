import json
import os
from collections import OrderedDict

class JsonMap:
	def create_empty(name):
		out = OrderedDict()
		out['map_name'] = name
		out['blocks'] = OrderedDict()
		out['entities'] = OrderedDict()
		out['background'] = []
		out['background_music'] = ''
		out['default_entry'] = [0, 64]

		return out

	def insert_block(dict, block, x, y):
		if (x,y) in dict.values():
			print("already exists!")
			return 
		if block == 'b' or block == 'brick':
			y = 'blockBreakableBrick'
		elif block == 'q' or block == 'question':
			y = 'blockQuestion'
		dict['blocks']



name = input("Enter name: ")
if not os.path.exists()


print(json.dumps(x))

map1 = "map1-1-1"