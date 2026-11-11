# AI 디자인 티 제거 기준 (Impeccable 카탈로그 impeccable.style/slop 중 인쇄 보고서 해당 항목)

검출: `python3 tools/detect_tells.py <html>` — 정적 검사. 수정 후 다시 돌려 0에 가깝게. 단 아래 "유지" 항목은 예외.

## A. 반드시 없앤다 (검출기 대상)
| 규칙 | 우리 시안의 예 | 바꾸는 법 |
|---|---|---|
| side-tab-border: 카드·인용·해설 상자 한쪽에 1px(0.3mm) 넘는 색 띠 | `.band3 .bl`, `.mx .rh`, 반영 전·후 `.q/.a`, 인라인 `border-left:1.2mm` | 띠를 지우고 ① 옅은 배경 면, ② 전체 0.25mm 헤어라인, ③ 앞번호·분야 칩·작은 색 점, ④ 아무것도 없음 중 하나. 분야 구분이 필요하면 칩/점으로 |
| accent-border-on-rounded: 둥근 카드 윗변 두꺼운 색 막대 | `.three3 div border-top:1.2mm` | 막대 제거, 카드 제목 글자색이나 작은 칩으로 구분, 카드 면은 배경으로 |
| hairline + wide shadow 동시 | — | 둘 중 하나. 인쇄물은 그림자 없이 |
| justified-text | `.tx p` 등 `text-align:justify` | `text-align:left` (한글 2단 좁은 단에서 자간이 벌어짐) |
| dash-in-headline / em-dash-overuse(한 쪽 2개 이상) | "…광장 — 문제는 …", "…아니었다 — 그늘의…" | 마침표·쉼표로 끊거나 문장을 다시 짠다. 헤드라인에는 대시 0, 본문은 쪽당 1개 이하 |
| forced-contrast: "X가 아니라 Y", "X만이 아니었다" 남발 | "사례의 겉모습이 아니라 작동한 조건을…" | 정보를 바로 말한다("사례에서 작동한 조건을 가져와…"). 대비 자체가 사실 정보일 때만 남기고 쪽당 1개 이하, 헤드라인 0 |

## B. 지면을 보고 판단한다 (육안 검토)
- **identical card grids / everything equal**: 같은 크기·같은 구성 카드 3–4개가 나란히 반복되는 쪽. 하나를 주인공으로 키우거나, 목록·문단·도식으로 형태를 바꿔 위계를 만든다.
- **hero metric 반복**: 큰 숫자+작은 라벨 띠(.tally, .st-nums, 수치 띠)가 연달아 나오는 쪽. 한 펼침면에 1회 이하, 숫자에는 맥락 한 줄.
- **status-chip soup**: 한 블록 안 칩이 4개 넘게 흩어진 경우. 분류에 꼭 필요한 칩(분야 칩, 가봉 판정 칩, 비교형/누적형)만 남긴다.
- **label above a heading (kicker)**: 카드·박스 제목 위에 영문/소문자 라벨을 또 얹어 제목을 반복하는 경우("TYPE A · 비교형 3곳" 위에 또 제목). 제목에 합치거나 지운다. 쪽 상단의 절 칩(.sec)은 장 내비게이션이라 유지.
- **numbered labels without sequence**: 순서 의미가 없는 01·02 번호. 단계·거점 번호(01–07)처럼 실제 순서·식별자면 유지.
- **icon tile stacked above heading**: 둥근 사각 아이콘 타일+제목 카드 반복. 아이콘을 제목 옆으로 붙이거나 타일 제거.
- **nested cards**: 카드 안 카드. 간격·괘선·글자 위계로 평평하게.
- **gray text on colored background / low contrast**: 색 면 위 회색 글자. 짙은 같은 계열 색이나 흰 글자로.
- **monotonous spacing**: 모든 블록 간격이 같은 쪽. 관련 묶음은 좁게, 묶음 사이는 넓게.
- **same text repeated in one container**: 한 상자 안 같은 라벨 반복.

## C. 유지 (티가 아님)
- 상단 nav 괘선, 표·수치 띠의 윗괘선(0.5mm 남색 + 0.25mm 회색)과 칸 구분선 — 편집 괘선.
- 장 간지의 그라데이션·대형 로마숫자, 사진 위 설명 말풍선(.st-co)의 그림자(사진 위 레이어 구분).
- 분야 4색, 붉은 더미, 가봉 판정 칩 3종.

공통 CSS에서 이미 처리: `.quote-slot`·`.st-next` 왼쪽 띠 제거, `.st-ec` 윗변 막대 제거, 한글 `word-break:keep-all`, 헤드라인 `text-wrap:balance`, 본문 `text-wrap:pretty`.
