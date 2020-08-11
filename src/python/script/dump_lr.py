# -*- coding: utf-8 -*-

import os
import sys
import io
import re
import copy
import math
import json
import re
from util import load_json, dump_json, filename_no_ext, TMP_COMPLEX, TMP_SPR
from generate_grid import gen_grids_and_dump, point_in_polygon

pnorm = os.path.normpath
pjoin = os.path.join

fp_remap = {
    pnorm("../png/haiguai2.png") : "dazhangyu_anim.json",
}

LAYER_BG = 0
LAYER_DECO = 1
LAYER_CITY = 2
LAYER_PATH = 4
PKG = 'worldmap/map'

GAME_LAYER_DECO = 2 # default
GAME_LAYER_CITY = 3 # bg_up
GAME_LAYER_COVER = 4 # cover
GAME_LAYER_TOP = 5 # top

ALL_COMPLEX = copy.deepcopy(TMP_COMPLEX)
ORDER = 0

context = {}

def pos_to_grid(x, y, unit_size):
    gx = int(math.floor(1.0 * x / unit_size))
    gy = int(math.floor(1.0 * y / unit_size))
    return gx, gy

def load_color(cstr):
    cint = int(cstr, 16)
    c = {}
    c['r'] = (cint & 0xff000000) >> 24
    c['g'] = (cint & 0x00ff0000) >> 16
    c['b'] = (cint & 0x0000ff00) >> 8
    c['a'] = (cint & 0x000000ff)
    return c

def dump_color(c):
    cint = (c['r'] << 24) + (c['g'] << 16) + (c['b'] << 8) + c['a']
    return '0x%08x' % cint

def add_color(c1, c2):
    c = {}
    c['r'] = min(c1['r'] + c2['r'], 255)
    c['g'] = min(c1['g'] + c2['g'], 255)
    c['b'] = min(c1['b'] + c2['b'], 255)
    c['a'] = min(c1['a'] + c2['a'], 255)
    return c

def multi_color(c1, c2):
    c = {}
    c['r'] = c1['r'] * c2['r'] // 255
    c['g'] = c1['g'] * c2['g'] // 255
    c['b'] = c1['b'] * c2['b'] // 255
    c['a'] = c1['a'] * c2['a'] // 255
    return c

def check_or_gen_base(base):
    if base == None:
        base = {
            "x scale" : 1.0,
            "y scale" : 1.0,
            "x shear" : 0.0,
            "y shear" : 0.0,
            "x" : 0,
            "y" : 0,
            "add color": load_color('0x00000000'),
            "multi color": load_color('0xffffffff'),
        }
    
    return base

def calc_base(spr, base):
    if not 'position' in spr:
        pos = { 'x': 0, 'y': 0 }
    else:
        pos = copy.deepcopy(spr['position'])
    
    p_angle = spr.get('angle', 0.0)
    sin_sv = math.sin(p_angle)
    cos_sv = math.cos(p_angle)
    off_x = -spr.get('x offset', 0)
    off_y = -spr.get('y offset', 0)
    off_rx = off_x * cos_sv - off_y * sin_sv - off_x
    off_ry = off_x * sin_sv + off_y * cos_sv - off_y

    if 'tag' in spr:
        base['tag'] = spr['tag']

    base_angle = base.get('angle' , 0.0)
    sin_v = math.sin(base_angle)
    cos_v = math.cos(base_angle)
    raw_x = pos['x'] + off_rx
    raw_y = pos['y'] + off_ry
    pos['x'] = raw_x * cos_v - raw_y * sin_v
    pos['y'] = raw_x * sin_v + raw_y * cos_v
    
    base['x'] = pos['x'] * base['x scale'] + base['x']
    base['y'] = pos['y'] * base['y scale'] + base['y']

    psx = spr.get('x scale', 1.0)
    psy = spr.get('y scale', 1.0)

    base_sx = base.get('x scale', 1.0)
    base_sy = base.get('y scale', 1.0)

    mul = 1.0
    if base_sx < 0:
        p_angle = math.pi - p_angle
        mul *= -1.0
    
    if base_sy < 0:
        p_angle = 2 * math.pi - p_angle
        mul *= -1.0

    base['angle'] = base.get('angle', 0.0) + p_angle

    base['x scale'] = psx * abs(base_sx)
    base['y scale'] = mul * psy * abs(base_sy)

    base['x shear'] = spr.get('x shear', 0.0) + base['x shear']
    base['y shear'] = spr.get('y shear', 0.0) + base['y shear']

    base['add color'] = add_color(base['add color'], load_color(spr.get('add color', '0x00000000')))
    base['multi color'] = multi_color(base['multi color'], load_color(spr.get('multi color', '0xffffffff')))

    return base

def check_tag(spr, tag):
    founded = False

    if 'tag' in spr:
        all_iter = re.finditer('layer=([a-zA-Z0-9_]+)', spr['tag'])
        count = 0
        for m in all_iter:
            count += 1
            if m.group(1) == tag:
                founded = True
                break
        
        if (tag == None or tag == '') and count == 0:
            founded = True
    else:
        if tag == '':
            founded = True
    
    return founded

def add_all_complex(base, dst_dir, fpath, spr):
    global TMP_SPR, ALL_COMPLEX

    if 'cloud' in fpath:
        return

    new_spr = copy.deepcopy(TMP_SPR)
    new_spr['filepath'] = os.path.relpath(fpath, dst_dir)
    new_spr['position'] = { 'x': base['x'], 'y': base['y'] }
    new_spr['x scale']  = base['x scale']
    new_spr['y scale']  = base['y scale']
    new_spr['x shear']  = base['x shear']
    new_spr['y shear']  = base['y shear']
    new_spr['angle'] = base['angle']
    new_spr['add color'] = dump_color(base['add color'])
    new_spr['multi color'] = dump_color(base['multi color'])
    new_spr['name'] = spr['name']
    ALL_COMPLEX['sprite'].append(new_spr)

def check_persistent(base, persistent):
    if not base.has_key('tag'):
        return False

    if not persistent:
        return False

    tag_str = base['tag']
    tag_list = tag_str.split(';')

    for tag in tag_list:
        if tag != '' and tag in persistent:
            return True
    
    return False

def add_rect_area(rect_area, base, export, extra_info=None, persistent=None):
    unit_size = rect_area['unit_size']
    
    if base.has_key('tag'):
        if base['tag'] == 'hai':
            print('tag = ' + base['tag'])
            if persistent != None:
                for k in persistent:
                    print(k)

    if check_persistent(base, persistent):
        key = 'persistent'
    else:
        gx, gy = pos_to_grid(base['x'], base['y'], unit_size)
        key = '%d_%d' % (gx, gy)

    if rect_area.has_key(key):
        area = rect_area[key]
    else:
        area = []
        rect_area[key] = area

    global ORDER

    info = {}
    info['position'] = { 'x': base['x'], 'y': base['y'] }
    info['x scale']  = base['x scale']
    info['y scale']  = base['y scale']
    info['x shear']  = base['x shear']
    info['y shear']  = base['y shear']
    info['angle'] = base['angle']
    info['add color'] = dump_color(base['add color'])
    info['multi color'] = dump_color(base['multi color'])
    info['export'] = export
    info['package'] = PKG
    info['order'] = ORDER
    ORDER += 1

    if extra_info:
        info['extra'] = extra_info

    area.append(info)

def dump_spr_boss(spr, export, base):
    if not 'tag' in spr:
        return

    if 'type=boss' in spr['tag']:
        return {
            'type' : 'boss'
        }

def dump_spr_city(spr, export, base):
    if not 'tag' in spr:
        return

    m = re.search(r'type=city(\d+)_?(\d+)?', spr['tag'])
    if not m:
        return
    
    global context
    cid_set = context['cid_set']
    city_list = context['city_list']

    groups = m.groups()
    cid = int(groups[0])

    if cid in cid_set:
        for v in city_list:
            if v['city_id'] == cid:
                data = v
                break
    else:
        cid_set.add(cid)
        pos = spr['position']
        data = {
            'city_id' : cid,
            'x' : pos['x'],
            'y' : pos['y'],
        }
        city_list.append(data)
    
    if len(groups) > 1:
        status = groups[1] and int(groups[1]) or 1
        if 'status' in data:
            status_arr = data['status']
        else:
            status_arr = []
            data['status'] = status_arr

        for _ in range(len(status_arr), status):
            status_arr.append('')
        status_arr[status - 1] = export
    else:
        data['export'] = export

    return False

def dump_spr_dynamic(spr, export, base):
    if not 'tag' in spr:
        return

    m = re.search(r'type=dyn_(\w+)?', spr['tag'])
    if not m:
        return
    
    global context, ORDER, PKG
    dynamic_dict = context['dynamic']

    name = m.group(1)

    info = {}
    info['position'] = { 'x': base['x'], 'y': base['y'] }
    info['x scale']  = base['x scale']
    info['y scale']  = base['y scale']
    info['x shear']  = base['x shear']
    info['y shear']  = base['y shear']
    info['angle'] = base['angle']
    info['add color'] = dump_color(base['add color'])
    info['multi color'] = dump_color(base['multi color'])
    info['export'] = export
    info['package'] = PKG
    info['order'] = ORDER
    ORDER += 1

    layer = GAME_LAYER_DECO
    m = re.search(r'layer=(\w+)', spr['tag'])
    if m:
        if m.group(1) == 'bg_up':
            layer = GAME_LAYER_CITY
        elif m.group(1) == 'cover':
            layer = GAME_LAYER_COVER
        elif m.group(1) == 'top':
            layer = GAME_LAYER_TOP
    info['layer'] = layer

    dynamic_dict[name] = info

    return False


def dump_spr_cloud(spr, export, base):
    basename = os.path.basename(spr['filepath'])
    if re.match(r'yun[0-9a-zA-Z]*(\.png|_complex\.json)$', basename):
        return {
            'type' : 'cloud',
        }

special_filter = [
    dump_spr_cloud,
    dump_spr_city,
    dump_spr_dynamic,
    dump_spr_boss
]

def dump_special_spr(spr, export, base):
    for filter in special_filter:
        info = filter(spr, export, base)
        if info == False:
            return False
        elif info:
            return info

def do_dump_spr(spr, src_dir, dst_dir, base, rect_area, layer_tag='', founded=False, persistent=None):
    global pjoin, pnorm
    global ORDER

    if not founded and not check_tag(spr, layer_tag):
        return

    fpath = pjoin(src_dir, spr['filepath'])
    bname = os.path.basename(fpath)
    fname = os.path.splitext(bname)[0]

    export = 'map_' + fname
    dst_bname = fname + '_complex.json'
    dst = pnorm(pjoin(dst_dir, dst_bname))
    
    if not os.path.exists(dst):
        spr_jval = copy.deepcopy(TMP_SPR)
        spr_jval['filepath'] = os.path.relpath(fpath, dst_dir)

        if '_anim' in export:
            spr_jval['name'] = 'anim'

        dst_jval = copy.deepcopy(TMP_COMPLEX)
        dst_jval['name'] = export
        dst_jval['sprite'].append(spr_jval)

        dump_json(dst, dst_jval)
    
    base = check_or_gen_base(base)
    base = calc_base(spr, base)

    extra_info = dump_special_spr(spr, export, base)

    if extra_info != False:
        add_rect_area(rect_area, base, export, extra_info, persistent)

    add_all_complex(base, dst_dir, fpath, spr)

def do_dump_group(spr, src_dir, dst_dir, base, rect_area, layer_tag='', founded=False, persistent=None):
    global pjoin, pnorm

    if not founded and not check_tag(spr, layer_tag):
        return

    base = check_or_gen_base(base)
    base = calc_base(spr, base)

    mid_path = spr['filepath']
    mid_dir = os.path.dirname(mid_path)
    spr['filepath'] = 'group'

    base_dir = pnorm(pjoin(src_dir, mid_dir))
    for sub_spr in spr['group']:
        if sub_spr.has_key('group'):
            do_dump_group(sub_spr, base_dir, dst_dir, copy.deepcopy(base), rect_area, layer_tag, True, persistent)
        else:
            do_dump_spr(sub_spr, base_dir, dst_dir, copy.deepcopy(base), rect_area, layer_tag, True, persistent)

def dump_city_spr(spr, src_dir, dst_dir):
    if not spr.has_key('tag'):
        return

    if spr.has_key('text'):
        return
    
    tag = spr['tag']
    m = re.search('city_id=([0-9]+)_?([0-9]+)?', tag)
    if not m:
        return

    filepath = pnorm(pjoin(src_dir, spr['filepath']))
    name_no_ext = filename_no_ext(os.path.basename(filepath))
    export = 'map_' + name_no_ext
    
    cid = int(m.group(1))
    pos = spr['position']
    ret = {
        'city_id': cid,
        'x': pos['x'],
        'y': pos['y'],
        'export': export,
    }
    
    dst_name = name_no_ext + '_complex.json'
    dst = os.path.join(dst_dir, dst_name)

    if not os.path.exists(dst):
        spr_jval = copy.deepcopy(TMP_SPR)
        spr_jval['filepath'] = os.path.relpath(filepath, dst_dir)

        dst_jval = copy.deepcopy(TMP_COMPLEX)
        dst_jval['name'] = export
        dst_jval['sprite'].append(spr_jval)

        dump_json(dst, dst_jval)

    return ret

def dump_city(spr, context, src_dir, out_json_dir):
    cid_set = context['cid_set']
    city_list = context['city_list']

    data = dump_city_spr(spr, src_dir, out_json_dir)
    if not data:
        return False

    cid = data['city_id']
    if cid in cid_set:
        print('[Error]: duplicated city_id:' + str(cid))
        # assert(False)
        return True

    cid_set.add(cid)
    city_list.append(data)
    return True

dump_unit_filters = [
    dump_city,
]

def dump_unit_info(spr, context, src_dir, out_json_dir):
    for filter in dump_unit_filters:
        if filter(spr, context, src_dir, out_json_dir):
            return True
            
    return False

def dump_unit(layer, context, src_dir, out_json_dir):
    if layer.has_key('sprite'):
        for spr in layer['sprite']:
            dump_unit_info(spr, context, src_dir, out_json_dir)

def point_in_area(area, x, y):
    vertices = area['vertices']
    return point_in_polygon(x, y, vertices)

def grid_in_area(area, gx, gy, unit_size):
    x1, y1 = gx * unit_size, gy * unit_size
    x2, y2 = x1 + unit_size, y1 + unit_size

    in_area = point_in_area(area, x1, y1) \
        or point_in_area(area, x2, y2) \
        or point_in_area(area, x1, y2) \
        or point_in_area(area, x2, y1)
    
    if in_area:
        return True
    
    grid_vec = {'x' : [x1, x1, x2, x2], 'y': [y1, y2, y2, y1]}
    vec_x = area['vertices']['x']
    vec_y = area['vertices']['y']

    for i in range(len(vec_x)):
        vx = vec_x[i]
        vy = vec_y[i]

        ok = point_in_polygon(vx, vy, grid_vec)
        if ok:
            return True
    
    quad = {'x': [x1, y1], 'y': [y1, y2]}
    vertices = area['vertices']
    vertices_x = vertices['x']
    vertices_y = vertices['y']
    for i in range(len(vertices_x)):
        x = vertices_x[i]
        y = vertices_y[i]
        if point_in_polygon(x, y, quad):
            return True
    
    return False

def calc_overlap_units(area, unit_size):
    overlap_units = []

    aabb = area['aabb']
    gx1, gy1 = pos_to_grid(aabb[0], aabb[1], unit_size)
    gx2, gy2 = pos_to_grid(aabb[2], aabb[3], unit_size)

    for gx in range(gx1, gx2 + 1):
        for gy in range(gy1, gy2 + 1):
            if grid_in_area(area, gx, gy, unit_size):
                overlap_units.append('%s_%s' % (gx, gy))
    
    return overlap_units

def get_min_max(v, min_v, max_v):
    if not min_v:
        min_v = v
    
    if not max_v:
        max_v = v

    return min(min_v, v), max(max_v, v)

def collect_area_info(layer):
    areas = {}
    entries = {}
    block2areas = {}
    areas['entries'] = entries
    areas['block2areas'] = block2areas

    if not 'shape' in layer:
        return areas
    
    for shape in layer['shape']:
        print('process area %s' % shape['name'])
        if shape['closed'] == False:
            print('area not closed')
            continue

        vertices = shape['vertices']
        len_vertices = len(vertices['x'])
        if len_vertices < 4:
            print('area len is less then 4')
            continue

        area = {}
        area['name'] = shape['name']
        area_vertices = {'x':[], 'y':[]}
        area_vertices_x = area_vertices['x']
        area_vertices_y = area_vertices['y']

        min_x, max_x = None, None
        min_y, max_y = None, None

        for i in range(len_vertices):
            x = int(vertices['x'][i])
            y = int(vertices['y'][i])

            if i > 0 and x == area_vertices_x[-1] and y == area_vertices_y[-1]:
                continue

            area_vertices_x.append(x)
            area_vertices_y.append(y)

            min_x, max_x = get_min_max(x, min_x, max_x)
            min_y, max_y = get_min_max(y, min_y, max_y)
        
        if area_vertices_x[0] == area_vertices_x[-1] and area_vertices_y[0] == area_vertices_y[-1]:
            area_vertices_x.pop()
            area_vertices_y.pop()
        
        area['vertices'] = area_vertices
        area['aabb'] = [min_x, min_y, max_x, max_y]
        area['overlap_unit'] = calc_overlap_units(area, 1024)

        for block_key in area['overlap_unit']:
            if not block_key in block2areas:
                block2areas[block_key] = []
            
            block_areas = block2areas[block_key]
            block_areas.append(area['name'])

        entries[area['name']] = area
    
    return areas

def try_mark_cloud(unit, area):
    vertices = area['vertices']
    for item in unit:
        pos = item['position']
        x = pos['x']
        y = pos['y']

        if not point_in_polygon(x, y, vertices):
            continue

        item['area'] = area['city_id']

def add_area_info_to_cloud(areas, top_val):
    for area in areas['entries'].values():
        for unit_key in area['overlap_unit']:
            if not unit_key in top_val:
                continue

            unit = top_val[unit_key]
            try_mark_cloud(unit, area)

def add_city_info_to_area(areas, city_val):
    entries = areas['entries']
    block2areas = areas['block2areas']
    cid2area = {}

    for city_info in city_val:
        cid = int(city_info['city_id'])
        is_activity_city = cid >= 10000
        if is_activity_city:
            continue

        x, y = city_info['x'], city_info['y']
        gx, gy = pos_to_grid(x, y, 1024)
        block_key = '%s_%s' % (gx, gy)
        if not block_key in block2areas:
            continue
        
        area_arr = block2areas[block_key]
        for area_name in area_arr:
            area = entries[area_name]
            vertices = area['vertices']
            if not point_in_polygon(x, y, vertices):
                continue

            cid2area[cid] = area
            area['city_id'] = cid
            break
    
    new_block2areas = {}
    for k in block2areas.keys():
        new_area_arr = []
        area_arr = block2areas[k]
        for area_name in area_arr:
            area = entries[area_name]
            if 'city_id' in area:
                new_area_arr.append(int(area['city_id']))
            else:
                print('bad area: no city in area %s' % area_name)
        
        new_block2areas[k] = new_area_arr
    
    areas['block2areas'] = new_block2areas
    areas['entries'] = cid2area

def dump_logic(out_json_dir, out_meta_dir, path, art_path, context):
    jval = load_json(path)
    if not jval:
        return
    
    src_dir = os.path.dirname(path)

    print('gen unit')
    dump_unit(jval['layer'][LAYER_CITY], context, src_dir, out_json_dir)

    city_dst = pjoin(out_meta_dir, 'city.json')
    dump_json(city_dst, context['city_list'])

    print('gen area')
    art_jval = load_json(art_path)
    areas = collect_area_info(art_jval['layer'][LAYER_PATH])

    city_json = pjoin(out_meta_dir, 'city.json')
    city_val = load_json(city_json)
    add_city_info_to_area(areas, city_val)

    top_json = pjoin(out_meta_dir, 'top.json')
    top_val = load_json(top_json)
    if top_val:
        add_area_info_to_cloud(areas, top_val)
        dump_json(top_json, top_val)

    dst_area = pjoin(out_meta_dir, 'area.json')
    dump_json(dst_area, areas)

    print('gen block')
    dst_grid = pjoin(out_meta_dir, 'block.json')
    gen_grids_and_dump(path, dst_grid)

def dump_layer(layer, src_dir, out_json_dir, out_meta_dir, meta_name, unit_size, layer_tag='', persistent=None):
    if not layer.has_key('sprite'):
        print('no sprite')
        return

    area_rect = {}
    area_rect['unit_size'] = unit_size

    for spr in layer['sprite']:
        if spr.has_key('group'):
            do_dump_group(spr, src_dir, out_json_dir, None, area_rect, layer_tag, persistent=persistent)
        else:
            do_dump_spr(spr, src_dir, out_json_dir, None, area_rect, layer_tag, persistent=persistent)

    dst = pnorm(pjoin(out_meta_dir, meta_name + '.json'))
    dump_json(dst, area_rect)

def dump_art(out_json_dir, out_meta_dir, path, context):
    jval = load_json(path)
    layers = jval['layer']

    src_dir = os.path.dirname(path)
    # print('dump layer bg')
    # dump_layer(layers[LAYER_BG], src_dir, out_dir, 'bg', 2048, persistent=('hai',))
    print('dump layer deco')
    dump_layer(layers[LAYER_DECO], src_dir, out_json_dir, out_meta_dir, 'deco', 1024)

    print('dump layer bg_up')
    dump_layer(layers[LAYER_DECO], src_dir, out_json_dir, out_meta_dir, 'bg_up', 1024, 'bg_up')

    print('dump layer cover')
    dump_layer(layers[LAYER_DECO], src_dir, out_json_dir, out_meta_dir, 'cover', 1024, 'cover')

    print('dump layer top')
    dump_layer(layers[LAYER_DECO], src_dir, out_json_dir, out_meta_dir, 'top', 1024, 'top')

    print('gen unit')
    dump_unit(layers[LAYER_DECO], context, src_dir, out_json_dir)

    dst = pjoin(out_meta_dir, 'dynamic.json')
    dump_json(dst, context['dynamic'])

    dst = pjoin(out_meta_dir, 'logic.json')
    logic = jval['size']
    dump_json(dst, logic)

def reset_context():
    context['cid_set'] = set()
    context['city_list'] = []
    context['dynamic'] = {}

def dump_lr(art_lr_file, logic_lr_file, out_json_dir, out_meta_dir):
    reset_context()
    dump_art(out_json_dir, out_meta_dir, art_lr_file, context)
    dump_logic(out_json_dir, out_meta_dir, logic_lr_file, art_lr_file, context)

def do_spr(spr, src_dir, dst_dir):
    global pjoin, pnorm

    ref_path = spr['filepath']
    norm_ref_path = pnorm(pjoin(src_dir, ref_path.replace('\\\\', '/')))
    new_ref_path = os.path.relpath(norm_ref_path, dst_dir)
    spr['filepath'] = new_ref_path

def do_group(spr, src_dir, dst_dir):
    global pjoin, pnorm

    mid_path = spr['filepath']
    mid_dir = os.path.dirname(mid_path)
    spr['filepath'] = 'group'

    base_dir = pnorm(pjoin(src_dir, mid_dir))
    for sub_spr in spr['group']:
        do_spr(sub_spr, base_dir, dst_dir)

def move_json(src, dst):
    fsrc = io.open(src, mode='r', encoding='GBK')
    jval = json.load(fsrc)
    fsrc.close()

    src_dir = os.path.dirname(src)
    dst_dir = os.path.dirname(dst)

    for spr in jval['sprite']:
        if not spr.has_key('group'):
            do_spr(spr, src_dir, dst_dir)
        else:
            do_group(spr, src_dir, dst_dir)

    fdst = open(dst, 'w')
    fstr = json.dumps(jval, sort_keys=True, indent=4, separators=(',', ': '))
    fdst.write(fstr)
    fdst.flush()
    fdst.close()

# def move_lr_result():
#     global OUT_JSON
#     global pnorm, pjoin

#     src_dir = OUT_JSON
#     dst_dir = PACK_DIR
#     include_types = { 
#         'complex' : True,
#         'anim' : True, 
#     }

#     p = re.compile('_([a-z]+).json')
#     for root, _, files in os.walk(src_dir):
#         for path in files:
#             m = p.search(path)
#             if not m:
#                 continue
            
#             t = m.group(1)
#             if t in include_types:
#                 continue
            
#             src = pnorm(pjoin(root, path))
#             rel = os.path.relpath(src, src_dir)
#             dst = pnorm(pjoin(dst_dir, rel))
#             move_json(src, dst)

if __name__ == '__main__':
    src_dir = '../data/daditu/json/'
    src_file = os.path.join(src_dir, 'test_2_complex.json')
    dst_dir = os.path.join(src_dir, 'test')
    jval = load_json(src_file)
    # dump_layer(jval, src_dir, dst_dir, 'test', 1024)

    print('gen all complex')
    dst = pjoin(dst_dir, 'all_complex.json')
    dump_json(dst, ALL_COMPLEX)