import sys, os
import subprocess
import re
import math
import argparse
import copy
import shutil
from PIL import Image
from util import load_json, dump_json, TMP_SPR

_exist = os.path.exists
_join = os.path.join
_basename = os.path.basename
_dirname = os.path.dirname

def fn_no_ext(path):
    bn = _basename(path)
    return os.path.splitext(bn)[0]

def _run_cmdv(*args):
    cmd = ' '.join(args)
    print(cmd)
    return subprocess.check_output(args)

def do_crop(im, src, dst_dir, x, y, w, h, unit_size):
    uw, uh = unit_size, unit_size
    if x + unit_size > w:
        uw = w - x
    if y + unit_size > h:
        uh = h - y

    bn = _basename(src)
    bn_info = os.path.splitext(bn)
    dst = _join(dst_dir, '%s_%dx%d+%d+%d%s' % (bn_info[0], uw, uh, x, y,bn_info[1]))

    print('crop png: ' + dst)
    crop = im.crop((x, y, x + uw, y + uh))
    crop.save(dst)

    return dst, uw, uh

def crop_png(src, dst_dir, unit_size):
    im = Image.open(src)
    w, h = im.size[0], im.size[1]

    ret = []

    x, y = 0, 0
    while x < w:
        while y < h:
            path, uw, uh = do_crop(im, src, dst_dir, x, y, w, h, unit_size)
            ret.append((path, x + uw / 2 - w / 2, h / 2 - y - uh / 2, uw, uh))
            y += unit_size
        x += unit_size
        y = 0
    
    return ret

def dump_png_to_bg_layer(layer, png_info, dst_dir):
    layer['sprite'] = []
    spr_arr = layer['sprite']

    for info in png_info:
        x = info[1]
        y = info[2] 
        spr = copy.deepcopy(TMP_SPR)
        spr['filepath'] = os.path.relpath(info[0], dst_dir)
        spr['position'] = { 'x' : x, 'y' : y }
        spr_arr.append(spr)

def clear_deco_layer(layer):
    for spr in layer['sprite']:
        if not 'tag' in spr:
            continue
        
        if 'layer=top' in spr['tag']:
            top = spr
            break
    
    layer['sprite'] = []
    spr_arr = layer['sprite']
    if top:
        spr_arr.append(top)

def clear_gen_pngs(src_png):
    src_dir = _dirname(src_png)
    src_base = _basename(src_png)
    fn_no_ext = os.path.splitext(src_base)[0]

    pstr = r'%s_\d+x\d+\+\d+\+\d+.png' % fn_no_ext
    p = re.compile(pstr)
    print('pstr = ' + pstr)

    for item in os.listdir(src_dir):
        if p.search(item):
            path = os.path.normpath(_join(src_dir, item))
            print('rm ' + path)
            os.remove(path)

def gen_lr(src, dst, png_info):
    dst_dir = _dirname(dst)

    jval = load_json(src)
    layers = jval['layer']

    dump_png_to_bg_layer(layers[0], png_info, dst_dir)
    # clear_deco_layer(layers[1])

    dump_json(dst, jval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('gen_lr')
    parser.add_argument('lr', type=str, help='lr path')
    parser.add_argument('png', type=str, help='png path')
    parser.add_argument('unit_size', type=int, help='unit_size')
    args = parser.parse_args(sys.argv[1:])

    if not _exist(args.lr):
        print('lr file not exists:' + args.lr)
        sys.exit(1)
    
    if not _exist(args.png):
        print('png file not exists:' + args.png)
        sys.exit(1)
    
    if args.unit_size <= 0:
        print('invalid unit_size: %d' % args.unit_size)
        sys.exit(1)
    
    clear_gen_pngs(args.png)
    png_info = crop_png(args.png, _dirname(args.png), args.unit_size)

    # lr_new_bn = _basename(args.lr)
    # lr_new_bn_info = os.path.splitext(lr_new_bn)
    # lr_new_dir = _dirname(args.lr)
    # lr_new = _join(lr_new_dir, lr_new_bn_info[0] + '_new' + lr_new_bn_info[1])
    gen_lr(args.lr, args.lr, png_info)
