import os
import sys
import re

idx = 0
arr = []
rev = {}
deref = {}
pp = re.compile(r'"filepath" *: *"([^"]*)"')

def get_idx(abs_path):
    global idx
    global arr
    global rev

    if rev.has_key(abs_path):
        return rev[abs_path]

    arr.append(abs_path)
    rev[abs_path] = idx
    idx += 1

    return idx - 1

def moveto(fpath_abs, target_abs):
    global rev
    global arr

    i = rev[fpath_abs]
    rev.pop(fpath_abs, None)
    rev[target_abs] = i
    arr[i] = target_abs

    print('idx = %d, move %s to %s' % (i, fpath_abs, target_abs))

def mark_file(fpath):
    global pp

    if not fpath.endswith('.json'):
        return

    f = open(fpath, 'r')
    lines = f.readlines()
    f.close()

    dirname = os.path.dirname(fpath)

    cnt = ''
    for line in lines:
        m = pp.search(line.strip())
        if m:
            ref_path = m.group(1)
            if not ref_path.isdigit() and ref_path != 'group':
                ref_path_abs = os.path.abspath(os.path.join(dirname, ref_path.replace('\\', '/')))
                ref_idx = get_idx(ref_path_abs)
                line = line.replace(ref_path, str(ref_idx))
                print('mark %s(abs %s) to %d' % (ref_path, ref_path_abs, ref_idx))

        cnt += line

    f = open(fpath, 'w')
    f.write(cnt)
    f.flush()
    f.close()

    print('mark file : %s' % fpath)

def resolve_file(fpath):
    global pp
    global arr

    print('try resovle: %s' % fpath)
    if not fpath.endswith('.json'):
        return

    f = open(fpath, 'r')
    lines = f.readlines()
    f.close()

    dirname = os.path.dirname(fpath)

    cnt = ''
    for line in lines:
        m = pp.search(line.strip())
        if m:
            ref_num = m.group(1)
            if ref_num.isdigit():
                ref_idx = int(ref_num)
                ref_path_abs = arr[ref_idx]
                ref_path_rel = os.path.relpath(ref_path_abs, dirname)
                ref_path_rel = ref_path_rel.replace(os.sep, r'\\')
                print('ref_num = %s\ndirname = %s\nref_path_abs = %s\nref_path_rel = %s' % (ref_num, dirname, ref_path_abs, ref_path_rel))
                line = line.replace(ref_num, ref_path_rel)

        cnt += line

    print('resovle write back: %s' % fpath)
    # print(cnt)

    f = open(fpath, 'w')
    f.write(cnt)
    f.flush()
    f.close()

def resolve_dir(dpath):
    global pp

    for root, dirs, files in os.walk(dpath):
        root_abs = os.path.abspath(root)

        for fn in files:
            fpath_abs = os.path.abspath(os.path.join(root, fn))

            if not fn.endswith('.json'):
                continue

            resolve_file(fpath_abs)


def find_ref(fpath_abs):
    global pp
    global deref

    # logflag = False
    # if fpath_abs == '/Volumes/rawres/res_ui/data/editor_data/icon_item/json/icon_item_heroexp_blue_complex.json':
    #     logflag = True
    #     print('proccessing %s' % fpath_abs)

    cur_idx = get_idx(fpath_abs)
    f = open(fpath_abs, 'r')
    lines = f.readlines()
    f.close()

    dirname = os.path.dirname(fpath_abs)

    for line in lines:
        m = pp.search(line)
        if not m:
            continue

        ref_path = m.group(1)
        if ref_path.isdigit() or ref_path == 'group':
            continue

        ref_path_abs = os.path.abspath(os.path.join(dirname, ref_path.replace('\\', '/')))
        ref_idx = get_idx(ref_path_abs)

        # if logflag:
        #     print('idx = %d, path = %s' % (ref_idx, ref_path_abs))

        if deref.has_key(ref_idx):
            deref_set = deref[ref_idx]
        else:
            deref_set = set()
            deref[ref_idx] = deref_set

        if not cur_idx in deref_set:
            deref_set.add(cur_idx)

def print_ref(path):
    global rev
    global arr
    global deref

    if not rev.has_key(path):
        print('no path : %s ' % path)
        return

    i = rev[path]
    if not deref.has_key(i):
        print('not ref : %s ' % path)
        return

    deref_set = deref[i]
    print('deref of %s:' % path)
    for di in deref_set:
        path = arr[di]
        print(path)

def check_file_ref(fpath_abs):
    global pp

    f = open(fpath_abs, 'r')
    lines = f.readlines()
    f.close()

    dirname = os.path.dirname(fpath_abs)
    
    for line in lines:
        m = pp.search(line)
        if not m:
            continue

        ref_path = m.group(1)
        ref_path = ref_path.replace('\\', '/')
    
        if ref_path == 'group':
            continue
    
        ref_path = os.path.join(dirname, ref_path)
        ref_path_abs = os.path.abspath(ref_path)
    
        if not os.path.exists(ref_path_abs):
            print('%s not found, ref by %s' % (ref_path_abs, fpath_abs))


def check_ref(path):
    if not os.path.exists(path):
        print('path not exists: %s' % path)
        return

    if os.path.isfile(path):
        check_file_ref(os.path.abspath(path))

    for root, dirs, files in os.walk(path):
        for fpath in files:
            if not fpath.endswith('.json'):
                continue

            fpath_abs = os.path.abspath(os.path.join(root, fpath))
            check_file_ref(fpath_abs)

    print('check completed')

def mk_idx(dpath):
    global pp
    # pt = re.compile(r'([^_]+)\.(json|png)$')

    for root, dirs, files in os.walk(dpath):
        for fn in files:
            fpath_abs = os.path.abspath(os.path.join(root, fn)).lower()
            get_idx(fpath_abs)

            if fn.endswith('.json'):
                find_ref(fpath_abs)
    
    print('process done')

def do_mv_file(p1, p2):
    global rev
    global arr
    global deref

    fpath_abs = os.path.abspath(p1).lower()
    target_abs = ''

    if os.path.isdir(p2):
        basename = os.path.basename(p1)
        target = os.path.join(p2, basename)
        target_abs = os.path.abspath(target)
    else:
        target_abs = os.path.abspath(p2)
       
    if not rev.has_key(fpath_abs):
        print('err path : %s' % fpath_abs)

    mark_file(fpath_abs)

    moved = set()

    cur_idx = get_idx(fpath_abs)
    if deref.has_key(cur_idx):
        deref_set = deref[cur_idx]
        moved.update(deref_set)
        for ref_idx in deref_set:
            ref_path_abs = arr[ref_idx]
            mark_file(ref_path_abs)

    moved.add(cur_idx)

    cmd = 'mv %s %s' % (fpath_abs, target_abs)
    print(cmd)
    if os.system(cmd) == 0:
        moveto(fpath_abs, target_abs)

    for midx in moved:
        path = arr[midx]
        resolve_file(path)

    print('completed')

def do_mv_batch(p1, p2):
    p = os.path.basename(p1)
    p = p.replace('*', '.*')

    dirname = os.path.abspath(os.path.dirname(p1)).lower()
    print('dirname = ' + dirname)

    for fbase in os.listdir(dirname):
        fbase = fbase.lower()
        fpath = os.path.join(dirname, fbase)
        if not os.path.isfile(fpath):
            continue

        m = re.search(p, fbase)
        if not m:
            continue

        print('file: %s' % fpath)
        do_mv_file(fpath, p2)

    print('mv batch completed')

def do_mv_dir(p1, p2):
    global rev
    global arr
    global deref

    if os.path.exists(p2):
        if not os.path.isdir(p2):
            print('%s is a file' % p2)
            return
    else:
        cmd = 'mkdir -p %s' % p2
        print(cmd)
        if os.system(cmd) != 0:
            return

    # dir_abs = os.path.abspath(dirname)
    moved = set()

    for root, dirs, files in os.walk(p1):
        target_rel = os.path.relpath(root, p1)
        target_dir = os.path.join(p2, target_rel)
        target_dir_abs = os.path.abspath(target_dir)
        
        if not os.path.exists(target_dir_abs):
            cmd = 'mkdir -p %s' % target_dir_abs
            print(cmd)
            os.system(cmd)

        for fn in files:
            fpath_abs = os.path.abspath(os.path.join(root, fn))
            target_abs = os.path.join(target_dir_abs, fn)

            mark_file(fpath_abs)

            cur_idx = get_idx(fpath_abs)
            if deref.has_key(cur_idx):
                deref_set = deref[cur_idx]
                moved.update(deref_set)
                for ref_idx in deref_set:
                    ref_path_abs = arr[ref_idx]
                    mark_file(ref_path_abs)

            moved.add(cur_idx)

            cmd = 'mv %s %s' % (fpath_abs, target_abs)
            print(cmd)
            if os.system(cmd) == 0:
                moveto(fpath_abs, target_abs)

    for midx in moved:
        path = arr[midx]
        resolve_file(path)
        
    print('completed')

def do_mv(p1, p2):
    if os.path.isdir(p1):
        do_mv_dir(p1, p2)
    elif os.path.isfile(p1):
        do_mv_file(p1, p2)
    else:
        do_mv_batch(p1, p2)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)
    
    dpath = sys.argv[1]

    if len(sys.argv) < 3 or sys.argv[2] != 'no_idx':
        mk_idx(dpath)

    pt = re.compile('mv ([^ ]*) ([^ ]*)')
    while True:
        cmd = raw_input().lower()
        if cmd == 'exit':
            break

        if cmd.startswith('mkdir '):
            os.system(cmd)
            continue

        if cmd.startswith('pr '):
            path = cmd[3:].strip()
            if path != '':
                print_ref(os.path.abspath(path))
                
            continue
        
        if cmd.startswith('ck '):
            path = cmd[3:].strip()
            if path != '':
                check_ref(os.path.abspath(path))

            continue


        m = pt.search(cmd)
        if not m:
            continue

        p1 = m.group(1)
        p2 = m.group(2)

        do_mv(p1, p2)

