#!/usr/bin/env python3
"""STYLE_2 기계 치환: v1 색값 → formal 팔레트. 사용: python3 restyle.py <파일...>  (css/html 제자리 수정)"""
import re, sys

MAP = {
    '#153A5E': '#1A2F4B', '#0F2C48': '#13243A',
    '#1597BE': '#2E5A87', '#0C7FA5': '#22476C',
    '#5BC0DE': '#7D97B3', '#7FC8E2': '#7D97B3', '#9CD3E7': '#A9BBCE', '#3BB2D6': '#2E5A87', '#7ACCE6': '#7D97B3',
    '#E4F3F9': '#E3E9F0', '#F2F9FC': '#F2F5F8', '#2A93D5': '#2E5A87',
    '#F5D33B': '#C9D7E6', '#FFF6CC': '#EEF2F6',
    '#2C5DA8': '#3A5F8E', '#1F9E83': '#3F7A6E', '#E39A2D': '#A67C45', '#8466C6': '#675F8C',
    '#137260': '#2F5E55', '#A8640E': '#7A5A2E', '#6B4E2E': '#5A4630', '#F6DDB6': '#EDE3D3',
    '#D9531E': '#2E5A87',
}
pat = re.compile('|'.join(re.escape(k) for k in MAP), re.I)

def run(path):
    s = open(path, encoding='utf-8').read()
    n = len(pat.findall(s))
    s = pat.sub(lambda m: MAP[m.group(0).upper()], s)
    # rgba 청록(21,151,190) → 블루(46,90,135), 노랑(245,211,59) → 옅은 블루
    s = re.sub(r'rgba\(\s*21\s*,\s*151\s*,\s*190', 'rgba(46,90,135', s)
    s = re.sub(r'rgba\(\s*245\s*,\s*211\s*,\s*59', 'rgba(201,215,230', s)
    open(path, 'w', encoding='utf-8').write(s)
    return n

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(f'{run(p):5d}  {p}')
