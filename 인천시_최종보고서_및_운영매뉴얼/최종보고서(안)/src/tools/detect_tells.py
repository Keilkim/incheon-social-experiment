#!/usr/bin/env python3
"""AI 디자인 티 검출기 (Impeccable 카탈로그 중 인쇄 보고서에 해당하는 규칙만, 정적 검사).
사용: python3 detect_tells.py <html> [<html> ...]   → 파일별 규칙 위반 위치 출력
"""
import re, sys, html as H

def css_blocks(src):
    # <style> 안 규칙 + 인라인 style 속성
    out = []
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', src, re.S):
        base = src[:m.start()].count('\n') + 1
        body = m.group(1)
        for r in re.finditer(r'([^{}]+)\{([^{}]*)\}', body):
            out.append((base + body[:r.start()].count('\n'), r.group(1).strip()[:60], r.group(2)))
    for m in re.finditer(r'style="([^"]*)"', src):
        out.append((src[:m.start()].count('\n') + 1, '(inline)', m.group(1)))
    return out

def mm(v):
    v = v.strip()
    m = re.match(r'([\d.]+)(mm|px|pt)?', v)
    if not m: return 0
    n = float(m.group(1)); u = m.group(2) or 'px'
    return n if u == 'mm' else n * 0.2646 if u == 'px' else n * 0.3528

def check(path):
    src = open(path, encoding='utf-8').read()
    hits = []
    for ln, sel, decl in css_blocks(src):
        for side in ('left', 'right'):
            for m in re.finditer(r'border-%s\s*:\s*([\d.]+(?:mm|px|pt)?)\s+(solid|dashed|dotted)\s+([^;]+)' % side, decl):
                if mm(m.group(1)) > 0.3 and 'transparent' not in m.group(3):
                    hits.append(('side-tab-border', ln, f'{sel} border-{side}:{m.group(1)}'))
        m = re.search(r'border-top\s*:\s*([\d.]+(?:mm|px|pt)?)\s+solid\s+([^;]+)', decl)
        if m and mm(m.group(1)) >= 0.8 and 'border-radius' in decl:
            hits.append(('accent-border-on-rounded', ln, f'{sel} border-top:{m.group(1)}'))
        if 'box-shadow' in decl and re.search(r'border\s*:\s*\.?[\d.]+', decl):
            hits.append(('hairline-border-wide-shadow', ln, sel))
        if re.search(r'background-clip\s*:\s*text', decl):
            hits.append(('gradient-text', ln, sel))
        if re.search(r'text-align\s*:\s*justify', decl):
            hits.append(('justified-text', ln, sel))
    # 본문 텍스트 검사(태그 제거, 주석·style·script 제외)
    body = re.sub(r'<!--.*?-->|<style.*?</style>|<script.*?</script>|<svg.*?</svg>', ' ', src, flags=re.S)
    pages = re.split(r'<section class="page', body)
    for pi, pg in enumerate(pages[1:], 1):
        txt = H.unescape(re.sub(r'<[^>]+>', '', pg))
        d = txt.count('—')
        if d >= 2: hits.append(('em-dash-overuse', f'page#{pi}', f'— {d}개'))
        for m in re.finditer(r'[^.。\n]{0,30}(?:이|가|은|는)?\s?아니(?:라|었다|다)[^.。\n]{0,30}', txt):
            hits.append(('forced-contrast', f'page#{pi}', m.group(0).strip()[:70]))
        for hl in re.findall(r'<h[12][^>]*class="hl"[^>]*>(.*?)</h[12]>', pg, re.S):
            t = H.unescape(re.sub(r'<[^>]+>', '', hl))
            if '—' in t: hits.append(('dash-in-headline', f'page#{pi}', t.strip()[:70]))
    # 중첩 카드: .card 안에 .card
    for m in re.finditer(r'class="[^"]*\bcard\b[^"]*"', src):
        seg = src[m.end():m.end() + 1500]
        close = seg.find('</div>')
        if 'class="card' in seg[:close] or re.search(r'class="[^"]*\bcard\b', seg[:close]):
            hits.append(('nested-cards', src[:m.start()].count('\n') + 1, 'card 안 card'))
    return hits

if __name__ == '__main__':
    total = {}
    for p in sys.argv[1:]:
        hs = check(p)
        print(f'## {p.split("/")[-1]}  ({len(hs)}건)')
        for rule, where, what in hs:
            total[rule] = total.get(rule, 0) + 1
            print(f'  {rule:28s} {str(where):>9s}  {what}')
    print('\n## 합계', total)
