#!/usr/bin/env python3
"""운영매뉴얼 문체·버전 검사 (MANUAL_BRIEF 7절 8항 + 기준 지면 규칙).

사용: python3 tools/check_manual.py [파일 ...]      (인자가 없으면 src/m*.html 전부)
출력: 쪽번호와 함께 위반을 적는다. [오류]는 고쳐야 하고, [확인]은 지면을 보고 판단한다.
끝 줄의 '오류 0'이 목표.
"""
import glob, os, re, sys
from html.parser import HTMLParser

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(SRC, 'm1_기획.html')
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
SKIP = {'style', 'script'}

# 5절 금지 문장
BANNED = [
    (r'(본|이) ?매뉴얼(은|에서는)', '메타 문장(본 매뉴얼은)'),
    (r'이 (편|절|장|쪽)(에서는|은|는)[^.]{0,40}(다룬다|정리한다|설명한다|소개한다|살펴본다)', '메타 문장(이 편/절에서는 ~다룬다)'),
    (r'(다룬다|설명한다)\.', '~확인: 메타 동사(다룬다·설명한다) — 책 소개 문장이면 지운다'),
    (r'로 단정하지 않는다', '"~로 단정하지 않는다"'),
    (r'추후 보완', '"추후 보완"'),
    (r'확인 ?필요', '"확인 필요"'),
    (r'원문', '"원문"'),
    (r'사용자 확인', '"사용자 확인"'),
    (r'\[(계획|증빙|제안|확인|추정)\]', '기록 상태 라벨'),
    (r'(계획|증빙|제안|추가 확인) 필요', '기록 상태 라벨'),
    (r'기준일', '"기준일"'),
    (r'핵심 포인트', '"핵심 포인트"'),
    (r'[\U0001F300-\U0001FAFF☀-⛿✀-➿]', '이모지'),
    (r'(하라|하세요|할 것)(\.|$|\s)', '명령형'),
    (r'것이 (좋다|바람직하다)', '권유형'),
    (r'목표(값|선)|달성|미달', '목표값·달성 표현(DECISIONS §3)'),
    (r'인천시항만공사|소상공인 ?325', '표기(인천항만공사·소상공인 365)'),
    (r'백마교', '굴포천 위치 표기(제1교량(부흥교) 옆 산책로)'),
    (r'누적형 ?5곳|교체 ?비교형 ?2곳', '1·2차 분류(비교형 3·누적형 4)'),
]
SD_PAGE = re.compile(r'(?<![A-Za-z0-9])p\.? ?\d{2,3}(?![0-9])')
DRAFT_CODE = re.compile(r'(?<![A-Za-z0-9])(C\d\d|T[ABH]\d\d|LT\d\d|L\d-\d\d)(?![0-9])')
FORM_NO = re.compile(r'서식\s?(\d{2})')
WHO_PAGES = {7, 9, 12, 15, 19, 23, 27, 29, 33, 37, 39, 42, 47, 49, 50, 52}
VSLOT_PAGES = WHO_PAGES | {1, 3, 5, 58, 64, 72, 75, 76}


class Node:
    __slots__ = ('tag', 'attrs', 'kids', 'parent', 'text', 'line')

    def __init__(self, tag, attrs, parent, line):
        self.tag, self.attrs, self.parent, self.kids, self.text, self.line = tag, dict(attrs), parent, [], '', line

    @property
    def cls(self):
        return set((self.attrs.get('class') or '').split())

    def all_text(self):
        out = [self.text]
        for k in self.kids:
            if isinstance(k, str):
                out.append(k)
            elif k.tag not in SKIP:
                out.append(k.all_text())
        return ''.join(out)

    def iter(self):
        for k in self.kids:
            if isinstance(k, Node):
                yield k
                yield from k.iter()

    def ancestors(self):
        p = self.parent
        while p is not None:
            yield p
            p = p.parent


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root', {}, None, 0)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur, self.getpos()[0])
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur, self.getpos()[0]))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, d):
        self.cur.kids.append(d)


def pno_of(sec, idx):
    for n in sec.iter():
        if 'pno' in n.cls:
            for k in n.kids:
                if isinstance(k, str) and k.strip():
                    return k.strip()
    return f'간지#{idx}'


def text_outside(node, skip_cls):
    out = []
    for k in node.kids:
        if isinstance(k, str):
            out.append(k)
        elif k.tag in SKIP or (k.cls & skip_cls):
            continue
        else:
            out.append(text_outside(k, skip_cls))
    return ''.join(out)


def norm(t):
    return re.sub(r'\s+', ' ', t.replace('⁠', '')).strip()


def check(path, ref_vs):
    src = open(path, encoding='utf-8').read()
    t = Tree()
    t.feed(src)
    name = os.path.basename(path)
    errs, notes = [], []
    E = lambda pg, m: errs.append(f'[오류] {name} {pg}쪽  {m}')
    W = lambda pg, m: notes.append(f'[확인] {name} {pg}쪽  {m}')

    vs = re.search(r'<script id="vscript">.*?</script>', src, re.S)
    if not vs:
        E('-', '버전 스크립트(<script id="vscript">)가 머리에 없음')
    elif ref_vs and norm(vs.group(0)) != norm(ref_vs):
        E('-', '버전 스크립트가 기준 지면(m1_기획.html)과 다름 → 그대로 복사할 것')
    if 'href="manual.css"' not in src:
        E('-', 'manual.css 링크 없음')

    secs = [n for n in t.root.iter() if n.tag == 'section' and 'page' in n.cls]
    if not secs:
        E('-', '<section class="page"> 없음')
    warn_total = 0
    for i, sec in enumerate(secs, 1):
        pg = pno_of(sec, i)
        body = norm(sec.all_text())
        if 'even' not in sec.cls and 'odd' not in sec.cls:
            E(pg, '쪽 클래스 even/odd 없음')
        if not ({'p1', 'p2', 'p3', 'p4', 'p5'} & sec.cls) and not ({'cover', 'front'} & sec.cls):
            W(pg, '편 클래스(p1–p5) 없음')
        if pg.isdigit():
            n = int(pg)
            if (n % 2 == 0) != ('even' in sec.cls):
                E(pg, f'쪽번호 {n}와 짝홀 클래스가 맞지 않음')

        # 1 금지 문장
        for rx, label in BANNED:
            for m in re.finditer(rx, body):
                ctx = f'…{body[max(0, m.start()-18):m.end()+12]}…'
                (W(pg, f'{label[4:]}: {ctx}') if label.startswith('~확인: ') else E(pg, f'{label}: {ctx}'))
        # 2 심의도서 쪽번호
        for m in SD_PAGE.finditer(body):
            E(pg, f'심의도서 쪽번호 노출 "{m.group(0)}"')
        # 3 초안 서식·근거 코드
        for m in DRAFT_CODE.finditer(body):
            E(pg, f'초안 코드 "{m.group(0)}"')
        # 4 헤드라인 대시·"아니라"
        for h in sec.iter():
            if 'hl' in h.cls:
                ht = norm(h.all_text())
                if re.search(r'[—–]|\s-\s', ht):
                    E(pg, f'헤드라인 대시: {ht}')
                if '아니라' in ht or '만이 아니' in ht:
                    E(pg, f'헤드라인 대비 문형: {ht}')
                if not ht.endswith('다'):
                    W(pg, f'헤드라인이 "~한다"로 끝나지 않음: {ht}')
                if len(ht) > 46:
                    W(pg, f'헤드라인 {len(ht)}자(40자 안팎·2줄 이내)')
        if body.count('—') >= 2:
            E(pg, f'본문 대시 {body.count("—")}개(쪽당 1개 이하)')
        if len(re.findall(r'아니라|만이 아니', body)) >= 2:
            E(pg, '"X가 아니라 Y" 문형 2개 이상')
        # 5 서식 번호: 체크리스트·서식 쪽 밖에서 3개 이상, 본문 문장 속
        is_form = bool({'p5'} & sec.cls) or any('form' in n.cls for n in sec.iter())
        outside = text_outside(sec, {'chk'})
        nums = set(FORM_NO.findall(outside))
        if not is_form and len(nums) >= 3:
            E(pg, f'서식 번호 {len(nums)}개({", ".join(sorted(nums))}) — 서식 연결 줄 쪽당 1–2개')
        for n in sec.iter():
            if n.tag in ('p', 'li', 'dd', 'td') and not ({'to-form', 'ref'} & n.cls) \
                    and not any({'to-form', 'chk', 'form', 'toc'} & a.cls for a in n.ancestors()):
                if FORM_NO.search(norm(text_outside(n, {'to-form', 'ref'}))) and not is_form:
                    E(pg, f'본문 문장 속 서식 번호: {norm(n.all_text())[:50]}')
        # 6·7 버전 블록
        for n in sec.iter():
            if 'data-v' in n.attrs:
                if not (n.parent is not None and 'vslot' in n.parent.cls):
                    E(pg, f'data-v="{n.attrs["data-v"]}" 블록이 .vslot 바로 안에 있지 않음 (줄 {n.line})')
                bad = set(n.attrs['data-v'].split()) - {'A', 'B', 'H'}
                if bad:
                    E(pg, f'data-v 값 오류 {bad}')
        for slot in [n for n in sec.iter() if 'vslot' in n.cls]:
            blocks = [k for k in slot.kids if isinstance(k, Node) and 'data-v' in k.attrs]
            cover = ' '.join(b.attrs['data-v'] for b in blocks).split()
            for v in 'ABH':
                if cover.count(v) != 1:
                    E(pg, f'.vslot(줄 {slot.line})에 {v} 블록이 {cover.count(v)}개')
            lens = [len(re.sub(r'\s', '', b.all_text())) for b in blocks]
            if len(lens) > 1:
                mean = sum(lens) / len(lens)
                if mean and max(abs(x - mean) / mean for x in lens) > 0.15:
                    E(pg, f'버전 블록 글자 수 차이 ±15% 초과 {dict(zip([b.attrs["data-v"] for b in blocks], lens))}')
            if 'who' in slot.cls:
                for b in blocks:
                    for dd in [x for x in b.iter() if x.tag == 'dd']:
                        if len(re.sub(r'\s', '', dd.all_text())) > 24:
                            E(pg, f'누가 하는가 {b.attrs["data-v"]} 칸 24자 초과: {norm(dd.all_text())}')
        if pg.isdigit():
            n = int(pg)
            has_who = any('who' in x.cls for x in sec.iter())
            if n in WHO_PAGES and not has_who:
                E(pg, '절 첫 쪽인데 누가 하는가 블록 없음')
            if has_who and n not in WHO_PAGES:
                E(pg, '배치표에 없는 쪽에 누가 하는가 블록')
            if any('vslot' in x.cls for x in sec.iter()) and n not in VSLOT_PAGES:
                E(pg, '배치표 밖 쪽에 버전 블록')
        # 기준 지면 규칙: 사례 박스·주의 상자·핵심 지침 띠·서식 연결 수
        cases = [x for x in sec.iter() if 'case' in x.cls]
        warns = [x for x in sec.iter() if 'warn' in x.cls]
        rules = [x for x in sec.iter() if 'rule' in x.cls]
        tofs = [x for x in sec.iter() if 'to-form' in x.cls]
        warn_total += len(warns)
        if len(cases) > 2: E(pg, f'인천 사례 박스 {len(cases)}개(쪽당 2개 이하)')
        if len(warns) > 1: E(pg, f'주의 상자 {len(warns)}개(쪽당 1개)')
        if len(rules) > 1: E(pg, f'핵심 지침 띠 {len(rules)}개(절마다 1개 이하)')
        if len(tofs) > 2: E(pg, f'서식 연결 줄 {len(tofs)}개(쪽당 최대 2개)')
        for c in cases:
            ct = norm(c.all_text())
            if not ct.startswith('인천에서는'):
                W(pg, '사례 박스 첫 줄이 "인천에서는"이 아님')
        if cases and not any('foot-src' in x.cls for x in sec.iter()):
            W(pg, '인천 사례가 있는데 자료 출처(.foot-src) 없음')
        # 레이블 금지(영문 키커)
        for m in re.finditer(r'\b(GUIDE|STEP|TIP|CHECK|POINT|NOTE)\b', body):
            E(pg, f'영문 라벨 "{m.group(0)}"')
    return errs, notes, warn_total


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(SRC, 'm[0-5]_*.html')))
    ref_vs = None
    if os.path.exists(REF):
        m = re.search(r'<script id="vscript">.*?</script>', open(REF, encoding='utf-8').read(), re.S)
        ref_vs = m.group(0) if m else None
    E, N, wt = [], [], 0
    for p in paths:
        e, n, w = check(p, ref_vs)
        E += e; N += n; wt += w
    if len(paths) > 1 and wt > 8:
        E.append(f'[오류] 주의 상자 전체 {wt}개(책 전체 8개 이하)')
    for line in E + N:
        print(line)
    print(f'\n검사 파일 {len(paths)}개 · 오류 {len(E)} · 확인 {len(N)}')
    sys.exit(1 if E else 0)


if __name__ == '__main__':
    main()
