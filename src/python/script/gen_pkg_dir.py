import shutil
import os
import re
import copy
from util import load_json, dump_json, TMP_COMPLEX, TMP_SPR

pjoin = os.path.join
pnorm = os.path.normpath

ROOT = '..'
TILE = pjoin(ROOT, 'tile')

def clear_bg_dirs(src_dir, name):
    pattern_str = '^%s_[0-9]+$' % name
    pattern = re.compile(pattern_str)

    for dir in os.listdir(src_dir):
        dir_path = os.path.join(src_dir, dir)
        if not os.path.isdir(dir_path):
            continue
        
        if pattern.search(dir_path):
            print('remove dir:' + dir_path)
            shutil.rmtree(dir_path)
    
def gen_bg_complex(json_dir, dst_png):
    basename = os.path.basename(dst_png)
    m = re.search(r'@(\d+)_(\d+)_(\d+)x(\d+)_([\d]+\.[\d]+)', basename)
    if not m:
        return
    
    x = int(m.group(1))
    y = int(m.group(2))
    w = int(m.group(3))
    h = int(m.group(4))
    s = float(m.group(5))

    spr = copy.deepcopy(TMP_SPR)
    spr['filepath'] = os.path.relpath(dst_png, json_dir)
    spr['x scale'] = 1 / s
    spr['y scale'] = 1 / s

    comp = copy.deepcopy(TMP_COMPLEX)
    comp['sprite'].append(spr)
    comp['name'] = 'bg'

    x_act = x / s
    y_act = y / s
    w_act = w / s
    h_act = h / s
    target_basename = 'bg_%d_%d_%dx%d_complex.json' % (x_act, y_act, w_act, h_act)
    filename = pjoin(json_dir, target_basename)
    dump_json(filename, comp)

    return { 
        'x': x_act,
        'y': y_act,
        'w' : w_act,
        'h' : h_act,
        'name' : 'bg',
    }

def gen_bg_dirs(gen_dir, name, out):
    all_bg = []

    count = 1
    src_dir = pjoin(TILE, name)

    for item in os.listdir(src_dir):
        path = pjoin(src_dir, item)
        if not os.path.isfile(path):
            continue
        
        if not item.endswith('.png'):
            continue
        
        out_name = '%s_%s' % (out, count)
        out_dir = pjoin(gen_dir, out_name)

        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        png_dir = pjoin(out_dir, 'png')
        json_dir = pjoin(out_dir, 'json')

        print("gen " + out_dir)

        if os.path.exists(png_dir):
            print('exist')

        os.makedirs(png_dir)
        os.makedirs(json_dir)

        dst_png = pjoin(png_dir, item)
        shutil.copy(path, dst_png)

        info = gen_bg_complex(json_dir, dst_png)
        info['dir'] = out_name
        all_bg.append(info)

        shutil.copy(path, dst_png)

        count += 1
    
    return all_bg
    
    # meta_json = pjoin(meta_dir, 'bg.json')
    # dump_json(meta_json, all_bg)

if __name__ == "__main__":
    TMP_EDITOR = '../tmp/editor_data'
    TMP_META = pjoin(TMP_EDITOR, 'meta')

    clear_bg_dirs(TMP_EDITOR)
    gen_bg_dirs(TILE, TMP_EDITOR, TMP_META)

