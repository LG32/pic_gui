import io
import os
import json

TMP_COMPLEX = {
    "name" : 'None',
    "sprite": [],
    "use_render_cache": False,
    "xmax": 0,
    "xmin": 0,
    "ymax": 0,
    "ymin": 0
}

TMP_SPR = {
    "camera": "perspective auto height",
    "filepath": "",
    "name": "_sprite",
    "position": {
        "x": 0,
        "y": 0,
    },
    "x offset": 0.0,
    "y offset": 0.0,
    "x scale": 1.0,
    "y scale": 1.0,
}

def load_json(src, encoding='GBK'):
    print('json src :' + src)
    if not os.path.exists(src):
        return None
    
    fsrc = io.open(src, mode='r', encoding=encoding)
    jval = json.load(fsrc)
    fsrc.close()

    return jval

def dump_json(dst, jval, encoding='GBK'):
	fstr = json.dumps(jval, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')).encode(encoding)
	dir_path = os.path.dirname(dst)
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)

	fout = open(dst, 'wb')
	fout.write(fstr)
	fout.flush()
	fout.close()

def filename_no_ext(fn):
    idx = fn.rfind('.')
    if idx == -1:
        return fn

    return fn[:idx]
