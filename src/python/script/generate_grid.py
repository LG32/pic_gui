import sys
import os
import json
import argparse
import math
import copy
from util import load_json, dump_json

LAYER_AREA = 5
LAYER_BLOCK = 6
GRID_SIZE = 50

MIN_X = 0
MAX_X = 0
MIN_Y = 0
MAX_Y = 0

col = 0
row = 0

TMP = {
	"camera" : "perspective auto height",
	"filepath" : "..\\png\\tree3.png",
	"name" : "_sprite94",
	"position" : 
	{
		"x" : 4384.062988281250,
		"y" : 1138.246948242188
	},
	"x offset" : 0,
	"x scale" : 0.4,
	"y offset" : 0,
	"y scale" : 0.4
}

# def load_json(path):
# 	fin = open(path, 'r')
# 	fstr = fin.read()
# 	fin.close()
# 	fstr = fstr.decode('GBK')
# 	src = json.loads(fstr)
# 	return src

# def dump_json(jval, path):
# 	fstr = json.dumps(jval, sort_keys=True, indent=4, separators=(',', ': ')).encode('GBK')
# 	dir_path = os.path.dirname(path)
# 	if not os.path.exists(dir_path):
# 		os.makedirs(dir_path)

# 	fout = open(path, 'w')
# 	fout.write(fstr)
# 	fout.flush()
# 	fout.close()

def check_path_or_exit(path):
	if not os.path.isfile(path):
		print('%s is not exits' % path)
		sys.exit(1)

def aabb(vertices):
	x_list = vertices['x']
	y_list = vertices['y']

	if len(x_list) < 1:
		return

	x1 = x_list[0]
	x2 = x_list[0]
	y1 = y_list[0]
	y2 = y_list[0]

	for i in range(1, len(x_list)):
		x = x_list[i]
		y = y_list[i]

		x1 = min(x, x1)
		x2 = max(x, x2)
		y1 = min(y, y1)
		y2 = max(y, y2)

	return x1, y1, x2, y2

def ceil(a, b):
	return int(math.floor(a / b))

def x2g(n):
	global GRID_SIZE
	return ceil(n, GRID_SIZE)

def grid_center(g):
	return g * GRID_SIZE + GRID_SIZE / 2

def grid_bound(g):
	return g * GRID_SIZE,  g * GRID_SIZE + GRID_SIZE

def intersect_right(x0, y0, x1, y1, x2, y2):
	if y1 > y2:
		x1, x2 = x2, x1
		y1, y2 = y2, y1

	if y0 < y1 or y0 >= y2:
		return False

	dx1 = x0 - x1
	dy1 = y0 - y1
	dx2 = x2 - x1
	dy2 = y2 - y1

	result = dx1 * dy2 - dx2 * dy1
	return result <= 0

def point_in_polygon(x, y, vertices):
	x_list = vertices['x']
	y_list = vertices['y']

	count = 0
	size = len(x_list)
	for i in range(size):
		x1 = x_list[i]
		y1 = y_list[i]

		i2 = (i + 1) % size
		x2 = x_list[i2]
		y2 = y_list[i2]

		# raycast from x, y towards right
		ok = intersect_right(x, y, x1, y1, x2, y2)
		if ok:
			count += 1

	return count % 2 == 1

def toidx(gx, gy):
	global col, row
	return (gx + col / 2) + (gy + row / 2) * col

def idxtogrid(idx):
	global col, row
	gy = idx / col - row / 2
	gx = idx - (gy + row / 2) * col - col / 2
	return gx, gy

def gen_grids(src):
	global col, row
	global GRID_SIZE

	jval = load_json(src)
	layer_list = jval['layer']

	size = jval['size']
	MAX_X = size['width'] / 2
	MIN_X = -MAX_X
	MAX_Y = size['height'] / 2
	MIN_Y = -MAX_Y

	col = abs(x2g(MIN_X)) + x2g(MAX_X) + 2
	row = abs(x2g(MIN_Y)) + x2g(MAX_Y) + 2
	print("col:%d, row:%d, total:%d" % (col, row, col * row))

	grid_size = col * row
	grids = [ 0 for i in range(0, col * row) ]
	grids_map = {}

	if len(layer_list) <= LAYER_BLOCK:
		return grids, grids_map

	layer = layer_list[LAYER_BLOCK]
	if not layer.has_key('shape'):
		return grids, grids_map

	for shape in layer['shape']:
		vertices = shape['vertices']
		x1, y1, x2, y2 = aabb(vertices)

		if x1 == None:
			break

		gx1 = x2g(max(x1, MIN_X))
		gx2 = x2g(min(x2, MAX_X)) + 1
		gy1 = x2g(max(y1, MIN_Y))
		gy2 = x2g(min(y2, MAX_Y)) + 1

		for gx in range(gx1, gx2):
			cx1, cx2 = grid_bound(gx)
			for gy in range(gy1, gy2):
				cy1, cy2 = grid_bound(gy)

				if not point_in_polygon(cx1, cy1, vertices) and \
					not point_in_polygon(cx1, cy2, vertices) and \
					not point_in_polygon(cx2, cy1, vertices) and \
					not point_in_polygon(cx2, cy2, vertices):
					continue

				idx = toidx(gx, gy)
				if idx >= grid_size:
					print('idx = ' + str(idx))

				grids[idx] = 1
				grids_map[idx] = True

	return grids, grids_map

def dump_grids(dst, grids_map):
	global col, row, GRID_SIZE

	blocks = []
	print('block size:' + str(len(grids_map.keys())))
	for k in grids_map:
		blocks.append(k)
	blocks.sort()
	
	result = {}
	result['col'] = col 
	result['row'] = row
	result['blocks'] = blocks
	result['grid_size'] = GRID_SIZE

	dump_json(dst, result)
	return result

def dump_test(src, grids_map):
	global TMP
	jval = load_json(src)
	point_layer = jval['layer'][3]
	sprite_list = []
	point_layer['sprite'] = sprite_list
	for k in grids_map:
		gx, gy = idxtogrid(k)
		cx = grid_center(gx)
		cy = grid_center(gy)

		data = copy.deepcopy(TMP)
		data['name'] = '_sprite' + str(100000000 + k)
		pos = data['position']
		pos['x'] = cx
		pos['y'] = cy
		sprite_list.append(data)

	dirname = os.path.dirname(src)
	basename = os.path.basename(src)
	newname = os.path.join(dirname, 'new_' + basename)
	print('dump to ' + newname)
	dump_json(newname, jval)

def gen_grids_and_dump(src, dst):
	check_path_or_exit(src)
	_, grids_map = gen_grids(src)
	return dump_grids(dst, grids_map)
	# dump_test(src, grids_map)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='generate grid')
	parser.add_argument('src', type=str, help='src path')
	parser.add_argument('dst', type=str, help='dst path')
	args = parser.parse_args(sys.argv[1:])

	src = args.src
	dst = args.dst

	check_path_or_exit(src)
	grids, grids_map = gen_grids(src)
	dump_grids(dst, grids_map)
	dump_test(src, grids_map)
