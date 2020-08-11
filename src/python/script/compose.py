
import cv2 as cv
import numpy as np
import math
import os
from util import load_json, dump_json

tmp_canvas = None

class transform:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.sx = 1
        self.sy = 1
        self.dirty = True
        self.mat = None

    def translate(self, x, y):
        self.x += x
        self.y += y
        self.dirty = True
    
    def rotate(self, angle):
        self.angle += angle
        self.dirty = True

    def scale(self, x, y):
        self.sx = x or 1
        self.sy = y or 1
        self.dirty = True
    
    def matrix(self):
        mat = self.mat
        if not self.dirty:
            return mat

        rad = self.angle / 180.0 * math.pi
        cosv = math.cos(rad)
        sinv = math.sin(rad)
        self.mat = np.array(([self.sx * cosv,    -sinv,              self.x],
                            [sinv,              self.sy * cosv,     self.y],
                            [0,                 0,                  1]))
        return self.mat

def gen_trans(spr):
    pos = spr['position']
    x, y = pos['x'], pos['y']
    sx, sy = spr.get('x scale', 1), spr.get('y scale', 1)
    angle = spr.get('angle', 0) / math.pi * 180.0

    trans = transform()
    trans.translate(x, y)
    trans.rotate(angle)
    trans.scale(sx, sy)

    return trans

def _set_max_aux(t, k, v):
    if t.has_key(k):
        t[k] = max(t[k], v)
    else:
        t[k] = v

def _set_min_aux(t, k, v):
    if t.has_key(k):
        t[k] = min(t[k], v)
    else:
        t[k] = v

def extend_border_spr(base_dir, spr, border, base_mat):
    trans = gen_trans(spr)
    local_mat = trans.matrix()
    mat = base_mat.dot(local_mat)

    print('base_mat')
    print(base_mat)
    print('local mat')
    print(local_mat)
    print('finale mat')
    print(mat)

    filepath = spr['filepath']
    filepath = os.path.join(base_dir, filepath)
    img = cv.imread(filepath, cv.IMREAD_UNCHANGED)

    shape = img.shape
    height = shape[0]
    width = shape[1]

    print(filepath, width, height)

    x1 = -width / 2
    x2 = x1 + width
    y1 = -height / 2
    y2 = y1 + height

    lb = np.array((x1, y1, 1))
    lt = np.array((x1, y2, 1))
    rt = np.array((x2, y2, 1))
    rb = np.array((x2, y1, 1))

    print(lb, lt, rt, rb)

    wlb = mat.dot(lb)
    wlt = mat.dot(lt)
    wrt = mat.dot(rt)
    wrb = mat.dot(rb)

    _set_min_aux(border, 'x1', min(wlb[0], wlt[0], wrt[0], wrb[0]))
    _set_min_aux(border, 'y1', min(wlb[1], wlt[1], wrt[1], wrb[1]))
    _set_max_aux(border, 'x2', max(wlb[0], wlt[0], wrt[0], wrb[0]))
    _set_max_aux(border, 'y2', max(wlb[1], wlt[1], wrt[1], wrb[1]))
    
    print(border)

def extend_border_group(base_dir, spr, border, base_mat):
    trans = gen_trans(spr)
    mat = trans.matrix()
    print('group base_mat')
    print(base_mat)
    print('group local mat')
    print(mat)

    filepath = spr['filepath']
    base_dir = os.path.join(base_dir, os.path.dirname(filepath))

    for sub_spr in spr['group']:
        extend_border_spr(base_dir, sub_spr, border, base_mat.dot(mat))

def calc_canvas_border(base_dir, comp, border):
    base_mat = np.identity(3)

    for spr in comp['sprite']:
        if spr.has_key('group'):
            extend_border_group(base_dir, spr, border, base_mat)
        else:
            extend_border_spr(base_dir, spr, border, base_mat)

def border_to_int(border):
    for k in border:
        v = border[k]
        if v < 0:
            border[k] = int(math.floor(v))
        else:
            border[k] = int(math.ceil(v))

def get_canvas_size(border):
    width = border['x2'] - border['x1']
    height = border['y2'] - border['y1']
    return width, height

def get_canvas_offset(border):
    return (-border['x1'], -border['y2'])

def add_weight_aux(canvas, new_canvas):
    sb, sg, sr, sa = cv.split(canvas)
    db, dg, dr, da = cv.split(new_canvas)

    da = da / 255.0
    sa = sa / 255.0

    rda = 1 - da
    nb = db * da + sb * rda 
    ng = dg * da + sg * rda 
    nr = dr * da + sr * rda 
    na = (1 - rda * (1 - sa)) * 255.0

    canvas = cv.merge((nb, ng, nr, na))
    canvas.astype('uint8')

    return canvas

def draw_spr(canvas, offset, spr, base_mat, base_dir):
    filepath = spr['filepath']
    filepath = os.path.join(base_dir, filepath)
    img = cv.imread(filepath, cv.IMREAD_UNCHANGED)

    shape = img.shape
    height = shape[0]
    width = shape[1]
    half_h = height / 2
    half_w = width / 2

    trans = gen_trans(spr)
    local_mat = trans.matrix()
    local_mat = local_mat.dot(np.array(([1, 0, -half_w], [0, 1, half_h], [0, 0, 1])))
    mat = base_mat.dot(local_mat)

    trans_mat = np.array(([1, 0, offset[0]], [0, 1, offset[1]]))
    affineMat = trans_mat.dot(mat)
    affineMat[1][2] = -affineMat[1][2]
    affineMat[0][1] = -affineMat[0][1]
    affineMat[1][0] = -affineMat[1][0]

    new_canvas = cv.warpAffine(img, affineMat, (canvas.shape[1], canvas.shape[0]))
    canvas = add_weight_aux(canvas, new_canvas)

    return canvas

def draw_group(canvas, offset, spr, base_mat, base_dir):
    trans = gen_trans(spr)
    mat = trans.matrix()

    filepath = spr['filepath']
    base_dir = os.path.join(base_dir, os.path.dirname(filepath))

    for sub_spr in spr['group']:
        canvas = draw_spr(canvas, offset, sub_spr, base_mat.dot(mat), base_dir)
    
    return canvas

def draw_complex(canvas, offset, comp, base_dir):
    base_mat = np.identity(3)

    for spr in comp['sprite']:
        if spr.has_key('group'):
            canvas = draw_group(canvas, offset, spr, base_mat, base_dir)
        else:
            canvas = draw_spr(canvas, offset, spr, base_mat, base_dir)
    
    return canvas

def draw_layer(canvas, offset, layer, base_dir):
    return draw_complex(canvas, offset, layer, base_dir)

def draw_lr(src):
    lr = load_json(src)
    layers = lr['layer']

    height = lr['size']['height']
    width = lr['size']['width']
    offset = (width / 2, -height / 2)
    base_dir = os.path.dirname(src)

    print('offset')
    print(offset)

    canvas = np.zeros((height, width, 4))
    print(canvas.shape)
    canvas = draw_layer(canvas, offset, layers[0], base_dir)
    canvas = draw_layer(canvas, offset, layers[1], base_dir)

    # for spr in comp['sprite']:
    #     if spr.has_key('group'):
    #         canvas = draw_group(canvas, offset, spr, base_mat, base_dir)
    #     else:
    #         canvas = draw_spr(canvas, offset, spr, base_mat, base_dir)
    
    return canvas


def main(src):
    global tmp_canvas

    comp = load_json(src)
    base_dir = os.path.dirname(src)

    # border = {}
    # calc_canvas_border(base_dir, comp, border)

    # border_to_int(border)
    # width, height = get_canvas_size(border)
    
    # offset = get_canvas_offset(border)

    # canvas = np.zeros((height, width, 4))
    # tmp_canvas = np.zeros((height, width, 4))
    # canvas = draw_complex(canvas, offset, comp, base_dir)
    canvas = draw_lr('../data/daditu/json/desert_lr.json')
    canvas = canvas.astype('uint8')

    cv.imwrite('test.png', canvas)
    print('success')
    # cv.imshow('haha', canvas)
    # cv.waitKey()

if __name__ == '__main__':
    path = '../data/editor_data/json/test_complex.json'
    main(path)
