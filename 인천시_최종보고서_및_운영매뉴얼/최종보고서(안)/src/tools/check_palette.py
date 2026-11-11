#!/usr/bin/env python3
"""STYLE_2 허용 팔레트 밖의 유채색 hex를 찾는다(저채도 회색·틴트는 통과). 사용: python3 check_palette.py <html/css...>"""
import re, sys
ALLOW = set(x.upper() for x in """
#1A2F4B #13243A #2E5A87 #22476C #7D97B3 #A9BBCE #E3E9F0 #F2F5F8 #C9D7E6 #EEF2F6 #D3DDE7
#3A5F8E #3F7A6E #A67C45 #675F8C #2F5E55 #7A5A2E #5A4630 #EDE3D3
#4F7396 #5B6B7A #7F8B96 #8C98A3
#E5332A #FBE9E8 #FF8A80
#FFFFFF #000000 #1E2A35 #2E3B47 #3D4A56 #56636E #5E6B77 #6A7784 #7D8892 #7F8E9B #8A949C #9AA6B1 #9AA8B5 #A2ADB6 #B5BEC6 #B8C4CD #B9C3CB #C9D1D8 #C9D3DC #D3DBE2 #D3DCE3 #D5DCE2 #DCE3E9 #E3E8EC #EEF1F4 #F1F3F5 #F3F6F8 #F7F9FA #FAFBFC
""".split())
def short(h):
    h = h.upper()
    return '#' + ''.join(c*2 for c in h[1:]) if len(h) == 4 else h
bad = 0
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'data:image/[^"\')]+', '', s)
    seen = {}
    for m in re.finditer(r'#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', s):
        h = short(m.group(0))
        if h not in ALLOW:
            r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
            mx, mn = max(r, g, b), min(r, g, b)
            sat = 0 if mx == 0 else (mx - mn) / mx
            # 채도 낮은 회색·옅은 틴트는 허용, 유채색(노랑·주황·초록·밝은 청록 등)만 잡는다
            if sat > 0.22 and not (mx > 0.9 and sat < 0.12):
                seen.setdefault(h, s[:m.start()].count('\n') + 1)
    for h, ln in sorted(seen.items(), key=lambda x: x[1]):
        bad += 1; print(f'{p.split("/")[-1]}:{ln}  {h}')
print(f'-- 팔레트 밖 색 {bad}종')
