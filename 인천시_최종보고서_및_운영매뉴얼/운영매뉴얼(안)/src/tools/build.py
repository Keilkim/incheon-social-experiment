#!/usr/bin/env python3
"""운영매뉴얼 전체 빌드: m0–m5의 <section class="page">를 순서대로 모아 src/manual_all.html을 만든다.

사용: python3 tools/build.py
- 파일 순서: m0_*.html → m1_*.html → … → m5_*.html (없는 파일은 건너뜀)
- 머리: manual.css 링크 + 버전 스크립트(기준 지면 m1_기획.html의 <script id="vscript">를 그대로 씀)
- 각 파일 <head>의 <style>은 파일 이름 주석과 함께 차례로 옮긴다(쪽 고유 스타일은 .pg07처럼 쪽 클래스로 묶을 것)
- 생성 파일은 손으로 고치지 않는다.
"""
import glob, os, re, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SRC, 'manual_all.html')
REF = os.path.join(SRC, 'm1_기획.html')

SEC_RE = re.compile(r'<section\s+class="page[\s"][^>]*>.*?</section>', re.S)
STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)
VS_RE = re.compile(r'<script id="vscript">.*?</script>', re.S)
ID_RE = re.compile(r'\sid="([^"]+)"')
PNO_RE = re.compile(r'<div class="pno">\s*(\d+)')


def files():
    out = []
    for i in range(6):
        hits = sorted(glob.glob(os.path.join(SRC, f'm{i}_*.html')))
        out += hits
    return out


def main():
    fs = files()
    if not fs:
        sys.exit('m0–m5 파일이 없다')
    vs = None
    for f in ([REF] if os.path.exists(REF) else []) + fs:
        m = VS_RE.search(open(f, encoding='utf-8').read())
        if m:
            vs = m.group(0)
            break
    if not vs:
        sys.exit('버전 스크립트(<script id="vscript">)를 찾지 못했다')

    styles, pages, warn, ids = [], [], [], {}
    for f in fs:
        src = open(f, encoding='utf-8').read()
        name = os.path.basename(f)
        head = src.split('<body', 1)[0]
        for st in STYLE_RE.findall(head):
            styles.append(f'/* ── {name} ── */\n{st.strip()}\n')
        secs = SEC_RE.findall(src)
        if not secs:
            warn.append(f'{name}: <section class="page"> 없음')
        for s in secs:
            pages.append((name, s))
            for i in ID_RE.findall(s):
                if i in ids and ids[i] != name:
                    warn.append(f'id 중복: "{i}" ({ids[i]}, {name}) → 파일 접두어를 붙일 것')
                ids.setdefault(i, name)

    # 쪽번호가 위치와 맞는지 (m0가 있어 1쪽부터 시작할 때만 판정)
    starts_at_1 = os.path.basename(fs[0]).startswith('m0_')
    for n, (name, s) in enumerate(pages, 1):
        m = PNO_RE.search(s)
        if m and starts_at_1 and int(m.group(1)) != n:
            warn.append(f'{name}: {n}번째 섹션의 쪽번호가 {m.group(1)}')

    html = ['<!doctype html>', '<html lang="ko">', '<head>', '<meta charset="utf-8">',
            '<title>인천 사회실험 운영매뉴얼</title>',
            '<!-- 생성 파일: tools/build.py가 m0–m5에서 모은다. 손으로 고치지 않는다. -->',
            '<link rel="stylesheet" href="manual.css">', vs,
            '<style>', *styles, '</style>', '</head>', '<body>']
    cur = None
    for name, s in pages:
        if name != cur:
            html.append(f'\n<!-- ======== {name} ======== -->')
            cur = name
        html.append(s)
    html += ['</body>', '</html>', '']
    open(OUT, 'w', encoding='utf-8').write('\n'.join(html))

    print(f'만듦: {OUT}')
    print(f'파일 {len(fs)}개 · 쪽 {len(pages)}개 (목표 76)')
    for f in fs:
        print('  ', os.path.basename(f), sum(1 for n, _ in pages if n == os.path.basename(f)), '쪽')
    for w in warn:
        print('주의:', w)


if __name__ == '__main__':
    main()
