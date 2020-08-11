import sys
import io
import argparse
from util import load_json
from bs4 import BeautifulSoup

if __name__ == '__main__':
    parser = argparse.ArgumentParser('dump_city_link')
    parser.add_argument('link_src', type=str)
    parser.add_argument('city_src', type=str)
    parser.add_argument('dst', type=str)

    args = parser.parse_args(sys.argv[1:])

    fsrc = io.open(args.link_src, mode='r', encoding='utf-8')
    soup = BeautifulSoup(fsrc.read(),features='lxml')
    fsrc.close()
    sheet = soup.find('worksheet', attrs={'ss:name': 'city_link'})

    rows = sheet.table.find_all('row')
    link_info = {}

    for i in range(3, len(rows)):
        cur_city_id = i - 2
        cells = rows[i].find_all('cell')

        count = 1
        for j in range(1, len(cells)):
            cell = cells[j]
            attrs = cell.attrs
            if 'ss:index' in attrs:
                link_city_id = int(attrs['ss:index']) - 1
            else:
                link_city_id = count
                count += 1
            
            if not cell.string or cell.string.strip() == '' or cur_city_id == link_city_id:
                continue
            
            print('link: city%d - city%d' % (cur_city_id, link_city_id))
            if cur_city_id < link_city_id:
                little, big = cur_city_id, link_city_id
            else:
                little, big = link_city_id, cur_city_id
            
            if not little in link_info:
                link_info[little] = []

            if not big in link_info[little]:
                link_info[little].append(big)
    
    city_info = load_json(args.city_src)
    city_map = {}
    for city in city_info:
        cid = city['city_id']
        city_map[cid] = city
    
    f = open(args.dst, 'w')
    cid_arr = sorted(link_info.keys())
    for cur_cid in cid_arr:
        linked_arr = link_info[cur_cid]
        linked_arr.sort()

        for linked_cid in linked_arr:
            link_data = cur_cid * 1000 + linked_cid
            cur_city = city_map[cur_cid]
            linked_city = city_map[linked_cid]
            f.write('%d, %d, %d, %d, %d\n' % (
                link_data, cur_city['x'], cur_city['y'], linked_city['x'], linked_city['y']))
    
    f.close()

    