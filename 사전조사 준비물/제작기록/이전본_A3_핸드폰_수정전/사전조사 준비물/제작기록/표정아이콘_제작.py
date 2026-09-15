"""인쇄용 5단계 표정. SVG 원본을 Chromium으로 투명 PNG로 내보낸다."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

OUT = Path(__file__).resolve().parents[1] / "표정아이콘"
SPECS = [
    ("01_red_very_bad", "매우 안 좋음", "#E85B61", "M 74 171 Q 128 104 182 171", False),
    ("02_orange_bad", "안 좋음", "#F39A46", "M 78 163 Q 128 128 178 163", False),
    ("03_yellow_neutral", "보통", "#F2CD4C", "M 80 157 L 176 157", False),
    ("04_green_good", "좋음", "#61B77B", "M 76 144 Q 128 191 180 144", False),
    ("05_blue_very_good", "매우 좋음", "#579BDE", "M 72 141 Q 128 156 184 141 C 178 205 78 205 72 141 Z", True),
]


def build():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=1)
        for name, label, color, mouth, delighted in SPECS:
            eyes = ('<path d="M 76 108 Q 88 90 100 108 M 156 108 Q 168 90 180 108" fill="none" stroke="#25364A" stroke-width="10" stroke-linecap="round"/>'
                    if delighted else '<circle cx="88" cy="105" r="10" fill="#25364A"/><circle cx="168" cy="105" r="10" fill="#25364A"/>')
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 256 256" role="img" aria-label="{label}">'
                   f'<circle cx="128" cy="128" r="112" fill="{color}"/>{eyes}'
                   f'<path d="{mouth}" fill="{"#25364A" if delighted else "none"}" stroke="#25364A" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>'
                   + ('<path d="M 91 153 Q 128 160 165 153" stroke="#fff" stroke-width="8" stroke-linecap="round" fill="none"/>' if delighted else '') + '</svg>')
            (OUT / f"{name}.svg").write_text(svg)
            page.set_content('<style>html,body{margin:0;background:transparent}svg{display:block}</style>' + svg)
            page.screenshot(path=str(OUT / f"{name}.png"), omit_background=True)
        browser.close()
    (OUT / "제작정보.json").write_text(json.dumps({"method": "SVG 원형·표정 선 직접 제작 → Chromium 투명 PNG 내보내기", "size": "1024×1024", "order": [{"file":n,"label":l,"color":c,"score":i} for i,(n,l,c,*_) in enumerate(SPECS,1)], "draft": "imagegen 내장 도구로 생성한 시안은 투명도 얼룩 때문에 최종 인쇄물에 사용하지 않음"}, ensure_ascii=False, indent=2))
    print(OUT)

if __name__ == "__main__":
    build()
