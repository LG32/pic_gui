
import sys
import os
import re
import io
import json
import argparse
from util import load_json

pngs = {}
pjoin = os.path.join
pnorm = os.path.normpath

def do_spr(spr, src_dir):
    global pjoin, pnorm, pngs

    ref_path = spr['filepath']
    if not ref_path.endswith('png'):
        return

    norm_ref_path = pnorm(pjoin(src_dir, ref_path.replace('\\\\', '/'))).lower()
    if not pngs.has_key(norm_ref_path):
        pngs[norm_ref_path] = True

def do_group(spr, src_dir):
    global pjoin, pnorm

    mid_path = spr['filepath']
    mid_dir = os.path.dirname(mid_path)
    spr['filepath'] = 'group'

    base_dir = pnorm(pjoin(src_dir, mid_dir))
    for sub_spr in spr['group']:
        if sub_spr.has_key('group'):
            do_group(sub_spr, base_dir)
        else:
            do_spr(sub_spr, base_dir)

def do_anim(src):
    jval = load_json(src)

    src_dir = os.path.dirname(src)
    for layer in jval['layer']:
        for frame in layer['frame']:
            if not 'actor' in frame:
                continue

            for actor in frame['actor']:
                do_spr(actor, src_dir)

def do_complex(src):
    jval = load_json(src)

    src_dir = os.path.dirname(src)
    for spr in jval['sprite']:
        if not 'group' in spr:
            do_spr(spr, src_dir)
        else:
            do_group(spr, src_dir)

def do_particle(src):
    jval = load_json(src)

    if not 'components' in jval:
        return
    
    src_dir = os.path.dirname(src)
    for comp in jval['components']:
        if not 'filepath' in comp:
            continue
        
        do_spr(comp, src_dir)


def do_json(fpath):
    m = re.search(r'_([a-z]+)*\.json', fpath)
    if not m:
        return

    t = m.group(1)

    if t == 'complex':
        do_complex(fpath)
    elif t == 'anim':
        do_anim(fpath)
    elif t == 'particle':
        do_particle(fpath)

def rm_unused_png(src_path, png_dir):
    global pngs
    pngs = {}

    if not os.path.exists(src_path):
        print('path not found:' + src_path)
        sys.exit(1)

    if not os.path.isdir(png_dir):
        print('path is not a dir: ' + png_dir)
        sys.exit(1)

    if os.path.isdir(src_path):
        for root, _, files in os.walk(src_path):
            for fpath in files:
                do_json(pjoin(root, fpath))
    else:
        do_json(src_path)
    
    print('------------------- rm_unused_png %s -------------------------------' % png_dir)

    for root, _, files in os.walk(png_dir):
        fpath = fpath.lower()
        for fpath in files:
            if not fpath.endswith('.png'):
                continue
            
            fpath = fpath.lower()
            fpath = pnorm(pjoin(root, fpath)).lower()
            if not fpath in pngs and os.path.exists(fpath):
                print('remove not ref png:' + fpath)
                os.remove(fpath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('src_path', type=str)
    parser.add_argument('png_dir', type=str)
    args = parser.parse_args(sys.argv[1:])

    src_path = args.src_path
    png_dir = args.png_dir

    rm_unused_png(src_path, png_dir)

