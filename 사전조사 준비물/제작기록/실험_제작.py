# -*- coding: utf-8 -*-
"""1차 · 2차 실험 준비물 · 「조사 방법 및 내용 등.hwpx」의 1차 · 2차 칸 기준
사전조사 조사지 부품(조사지_제작.py)을 그대로 가져다 쓴다."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import 조사지_제작 as M
C, B, MU = M.C, M.B, M.M
BASE = C.ROOT.parent
ORIG_FRAME = M._frame
F5 = ["1", "2", "3", "4", "5"]


def mixed(items, path, footer):
    return C.render_mixed(items, path, extra_css=M.CSS, footer=footer)


def board_pdf(html, path, size):
    return C.render([html], path, size=size, margin=(10, 10, 10, 10), extra_css=M.BOARD_CSS)


def badge(n):
    where = {1: "출발", 2: "중간", 3: "중간", 4: "도착"}[n]
    return (f"<span style='display:inline-block;text-align:center;border:2px solid {B};border-radius:6px;padding:1px 12px 3px;"
            f"color:{B};line-height:1.05;vertical-align:bottom'><span style='font-size:8pt;display:block'>{where}</span>"
            f"<span style='font-size:26pt;font-weight:700'>{n}</span></span>")


def seonin(r):
    return M.seonin(phase=r)


def songdo(r):
    acts = ["걷기", "달리기", "뛰다가 숨고르기", "구경하기", "휴대폰하고 놀기"] + (["매개 요소 이용"] if r == 2 else [])
    p1 = (M.hd("송도", "러닝존 기록지")
          + M.st([("내 구간", "□ 출발 &nbsp;□ 코스 &nbsp;□ 쉼터 &nbsp;□ 횡단보도")])
          + "<div class='how'>내 구간에 들어온 사람을 한 줄씩 적습니다(원 조사표: 어떤 행태를 구간별로 가지는지). " + M.GROUP_RULE
          + ". 행위는 해당하면 모두 ✓, 그 밖의 행동은 비고에." + (" <b>매개 요소 이용</b>은 2차에 새로 둔 소통 요소를 쓴 경우입니다." if r == 2 else "") + "</div>"
          + M.gcheck([("인원수", "비우면 1", 46, ""), ("시각", "00:00:00", 80, "")], "행위", acts, rows=25, w_no=28, w_memo=100, row_h=7.9))
    if r == 1:
        qs = [("Q1", "러닝 코스가 생긴 뒤 사람들 사이의 소통이 늘었다고 느끼나요?", "O / △ / X", "Do you feel the running course helped people interact more?"),
              ("Q2", "왜 그렇게 느끼세요?", "O나 X로 답했을 때 · 말 그대로", "Why do you feel that way?"),
              ("Q3", "소통이 더 생기려면 무엇이 있으면 좋을까요?", "말 그대로", "What would help people connect more?")]
    else:
        qs = [("Q1", "러닝 코스와 새로 둔 소통 요소 덕분에 소통이 늘었다고 느끼나요?", "O / △ / X", "Do you feel the course and the new elements helped people interact more?"),
              ("Q2", "왜 그렇게 느끼세요?", "O나 X로 답했을 때 · 말 그대로", "Why do you feel that way?"),
              ("Q3", "어떤 요소가 가장 도움이 됐나요?", "말 그대로", "Which element helped the most?")]
    p2 = (M.hd("송도", "인터뷰 기록표", "조사 중간에 누구에게나 · 1분")
          + M.card("읽어 줄 질문 · O 그렇다 · △ 잘 모르겠다 · X 아니다 · 원 조사표: " + ("러닝 코스 마련이 소통을 증진시켰다고 느끼는지" if r == 1 else "러닝 코스 + 매개 요소 마련이 소통을 증진시켰다고 느끼는지"), qs)
          + "<style>.iv table.qr tr.r td{height:6.6mm}</style><div class='iv'>"
          + M.qrec([("Q1 소통", "O / △ / X", 62), ("Q2 이유", "말 그대로", None), ("Q3 " + ("더 필요한 것" if r == 1 else "도움된 요소"), "말 그대로", None)],
                   rows=25, w_memo=60, sample_size=50) + "</div>" + M.count_line("말 건 사람", "거절", "말이 안 통함"))
    if r == 1:  # 참가자 모집 폼은 사전조사 때 연다 → 「사전조사 준비물/03_송도」 11쪽
        return [("A4", p1), ("A4", p2)]
    gq = [("①", "다음 러닝 활동(2차)에도 참여하시겠어요?", "예 / 아니오 / 잘 모르겠음 · 원 조사표: 재참여 의사(구글폼 수집)", ""),
          ("②", "1차 러닝 활동에 참여하셨나요?", "예(참가번호) / 아니오", ""),
          ("③", "혼자 오시나요, 아는 사람과 함께 오시나요?", "혼자 / 함께(몇 명)", ""),
          ("④", "연락처", "운영용 · 분석에 쓰지 않음", "")]
    p3 = (M.hd("송도", "구글폼 문항표", "폼에 그대로 옮겨 씀")
          + M.card("구글폼 문항 · 한국어 · 영어로 함께 만듭니다", gq)
          + "<div class='tip'>재참여 ‘의사’(이 폼)와 실제로 다시 온 것(같은 참가번호의 출석)을 따로 셉니다.</div>")
    return [("A4", p1), ("A4", p2), ("A4", p3)]


def rodeo(r):
    cols = [("시각", "시:분", 56, ""), ("어디서", "", 140, "부스 안 · 벤치 · 그 밖"), ("몸 방향", "안쪽 = 부스 안쪽", 110, "안쪽 · 바깥 · ?"),
            ("꽁초", "", 150, "부스 수거함 · 바닥 · 그 밖 · ?")]
    if r == 2:
        cols.append(("사인 보고 왔나", "다 피운 뒤 물어서", 90, "예 · 아니오 · ?"))
    how = ("담배 피우는 사람 <b>한 명 = 한 줄</b>, 해당하는 것에 <b>동그라미</b>(원 조사표: 부스 안에서 피우는지 · 부스 내부를 향하는지 · "
           "부스 안 수거함에 버리는지). 몸 방향은 피우는 중간에 한 번 봅니다. 꽁초를 끝까지 못 봤으면 ?.")
    if r == 2:
        how += " 다 피우고 나오는 사람에게 “안내 사인을 보고 찾아오셨어요?”라고 묻고, 안 물었으면 비워 둡니다."
    return [("A4", M.hd("로데오거리", "담배 피우는 사람 기록지") + f"<div class='how'>{how}</div>"
             + M.pcheck(cols, rows=26, w_no=28, w_memo=90 if r == 2 else 120, row_h=8.2, memo="비고", sample_size=C.RODEO_EXPERIMENT_SAMPLE_SIZE))]


def terminal(r):
    p1 = (M.hd("연안여객터미널 ①", "2층에서 쉬는 사람 기록지", "2층 담당")
          + "<div class='how'>2층 일반 휴식 구역에 <b>앉는 사람마다 한 줄</b>(원 조사표: 2층 휴식 인원 수 및 시간 체크). 시각은 <b>00:00:00</b>, "
            "자리 위치는 좌석 배치도의 <b>의자 번호</b>. 만족도 · 위생 안심도는 스티커 보드로 받으니 여기서는 묻지 않습니다. 직원 · 전용공간 이용자는 적지 않습니다.</div>"
          + M.pcheck([("앉은 시각", "00:00:00", 90, ""), ("일어난 시각", "00:00:00", 94, ""), ("자리 위치", "의자 번호", 80, "")],
                     rows=26, w_no=30, w_memo=200, row_h=8.2, memo="비고"))
    p2 = M.terminal()[1][1].replace("1층 담당 · 사전조사 · 15분마다", "1층 담당 · 15분마다")
    return [("A4", p1), ("A4", p2)]


def china_web():
    items = [("QR 접속", "안내판 QR로 첫 화면이 열린 수 · 운영자 시험 접속은 뺌", "인지성 · QR 클릭 수"),
             ("에티켓 확인", "에티켓 화면을 열고 확인한 수", "지각성"),
             ("확인 시간차", "첫 화면 → 에티켓 확인까지 걸린 시간(초) · 중앙값", "지각성 · 랜딩페이지-에티켓 확인 시간차"),
             ("좋아요 · 나빠요", "에티켓 아래 버튼 · 둘 다 누르지 않으면 ‘무응답’(무관심으로 단정하지 않음)", "호감도")]
    t1 = ("<table><colgroup><col style='width:110px'><col><col style='width:200px'></colgroup>"
          "<thead><tr><th>웹에 남길 것</th><th>어떻게</th><th>원 조사표</th></tr></thead><tbody>"
          + "".join(f"<tr><td style='font-weight:700;color:{B}'>{a}</td><td>{b}</td><td style='color:{MU}'>{c}</td></tr>" for a, b, c in items)
          + "</tbody></table>")
    heads = ["날짜", "QR 접속", "에티켓 확인", "확인 시간 중앙값(초)", "좋아요", "나빠요", "무응답", "비고"]
    body = "".join("<tr class='r'>" + "<td></td>" * len(heads) + "</tr>" for _ in range(14))
    t2 = ("<table class='tl'><thead><tr>" + "".join(f"<th>{h}</th>" for h in heads) + f"</tr></thead><tbody>{body}</tbody></table>")
    return [("A4", M.hd("차이나타운", "QR 웹 기록 정리표", "사무실 · 날마다 한 줄")
             + "<div class='how'>원 조사표 2차 칸은 현장 설문 없이 <b>웹 기록</b>으로 봅니다. QR 안내판의 모바일 화면이 아래 네 가지를 자동으로 남기게 만들고, "
               "날마다 합계를 옮겨 적습니다. 세션 수는 사람 수가 아닙니다.</div>" + t1
             + f"<div style='font-size:11pt;font-weight:700;color:{B};margin:10px 0 4px'>날마다 옮겨 적기</div>" + t2)]


def overview(r):
    rows = {
        1: [("약산초등학교", "설문(발송)", "시민안 표식 사진을 보고 봤는지 · 어디서 · 어떻게 말할지 + 워크숍 결과", "01_약산초등학교 (지도 · 설문지 · 워크숍 기록표)"),
            ("선인재단", "주요 이용 동선(진입부) · 통과 시간(구간별) · 표정 등(구간별)", "4개 위치별 기록지: 학생별 특징 · 시각 · 동선 · 행태 · 표정", "02_선인재단 (위치별 8장 · 총 32장)"),
            ("송도", "참여 의사(구글폼) · 소통 증진 인터뷰 · 구간별 행태", "러닝존 기록지 · 인터뷰 50명 · 참여 의사는 사전조사 때 연 모집 구글폼 응답", "03_송도 (10쪽)"),
            ("차이나타운", "호감도 · 인지도 · 이미지 2지선다 (사전 · 1차 칸)", "스티커 보드 Q1~Q4 · 그림 A = 1차 실험 안내판", "04_차이나타운_폼보드"),
            ("굴포천", "카메라 고정 녹화 · 이용 행태 · 매력도 · 만족도 · 기대감 + 다른 하부공간(스티커)", "머무는 사람 기록지 · 스티커 보드 4문항", "05_굴포천 · 05_굴포천_폼보드"),
            ("로데오거리", "부스 수거함에 버리는지 · 부스 안 흡연 · 부스 안쪽 방향", "담배 피우는 사람 기록지 · 500명", "06_로데오거리 (20장)"),
            ("연안여객터미널", "2층 휴식 인원 · 시간 · 짐 보관 안팎 · 위생 안심도 · 공간 만족도(스티커)", "2층 기록지 · 1층 캐리어 15분 · 스티커 보드 2문항", "07_연안여객터미널 · 07_연안여객터미널_폼보드")],
        2: [("약산초등학교", "설문(발송)", "어린이안 표식 사진을 보고 봤는지 · 어디서 · 어떻게 말할지", "01_약산초등학교 (지도 · 설문지)"),
            ("선인재단", "주요 이용 동선(진입부) · 통과 시간(구간별) · 표정 등(구간별)", "1차와 같은 위치별 8장 · 총 32장", "02_선인재단 (위치별 8장 · 총 32장)"),
            ("송도", "재참여 의사(구글폼) · 코스 + 매개 요소 소통 인터뷰 · 구간별 행태", "러닝존 기록지(+ 매개 요소 이용) · 인터뷰 50명 · 구글폼 문항", "03_송도 (11쪽)"),
            ("차이나타운", "좋아요/나빠요 · QR 클릭 수 · 에티켓 확인 시간차 (2차 칸)", "현장 설문 없음 · 웹 기록을 날마다 정리", "04_차이나타운_웹기록"),
            ("굴포천", "1차와 같음", "머무는 사람 기록지 · 스티커 보드 4문항", "05_굴포천 · 05_굴포천_폼보드"),
            ("로데오거리", "부스 안 흡연(유도사인 보고 왔는지 설문 포함) · 부스 안쪽 방향 · 부스 수거함", "기록지(+ 사인 보고 왔나) · 500명", "06_로데오거리 (20장)"),
            ("연안여객터미널", "1차와 같음", "2층 기록지 · 1층 캐리어 15분 · 스티커 보드 2문항", "07_연안여객터미널 · 07_연안여객터미널_폼보드")]}[r]
    tr = "".join(f"<tr><td style='font-weight:700;color:{B};vertical-align:middle'>{a}</td>" + "".join(
        f"<td style='font-size:9pt;line-height:1.45;vertical-align:middle'>{x}</td>" for x in rest) + "</tr>" for a, *rest in rows)
    return [("A4L", M.hd("한눈에", f"{r}차 실험 한눈에", "원 조사표 「조사 방법 및 내용 등」 기준")
             + "<table><colgroup><col style='width:110px'><col><col><col style='width:200px'></colgroup>"
               f"<thead><tr><th>거점</th><th>원 조사표 ({r}차 칸)</th><th>보는 것 · 묻는 것</th><th>뽑을 종이</th></tr></thead><tbody>{tr}</tbody></table>"
             + "<div class='legend' style='font-size:8.8pt'>적는 방식은 사전조사와 같습니다 — 한 줄 = 혼자 온 사람 또는 무리(인원수 비우면 1) · 시각 00:00:00 · "
               "해당하면 ✓ · 스티커는 직접 세서 기록 · 조사원 수칙은 「사전조사 준비물/00_조사원수칙」을 그대로 씁니다.</div>")]


def build(r):
    lab = f"{r}차 실험"; D = BASE / lab; D.mkdir(exist_ok=True)
    for sub, txt in [("약산초_사진", f"{r}차 약산초 설문지에 들어갈 표식 사진 · 1.jpg ~ 6.jpg (세로로 긴 사진) · 넣고 다시 뽑으면 프레임에 들어갑니다."),
                     ("약산초_지도", "비워 두면 「사전조사 준비물/약산초_지도」를 그대로 씁니다. 후보 위치가 바뀌었을 때만 지도.jpg · 번호.txt를 넣으세요.")] + (
            [("차이나타운_그림", "1차 보드 Q2 그림 · A.jpg = 1차 실험 안내판(정답), B.jpg = 대조 그림 · 넣고 다시 뽑으면 들어갑니다.")] if r == 1 else []):
        (D / sub).mkdir(exist_ok=True); (D / sub / "여기에 넣으세요.txt").write_text(txt + "\n")
    M._yaksan_photo = lambda i, lab=lab: M._img_src(f"../{lab}/약산초_사진", str(i))
    M._frame = lambda folder, *a, lab=lab, **k: ORIG_FRAME(f"../{lab}/{folder}", *a, **k)
    M.MAP_DIRS = [D / "약산초_지도", C.ROOT / "약산초_지도"]
    y = [M.yaksan_map()] + M.yaksan()  # 동네 지도 + 설문지 + 워크숍 기록표 (모두 세로)
    out = [mixed(overview(r), D / "00_한눈에.pdf", lab),
           mixed(y if r == 1 else y[:2], D / "01_약산초등학교.pdf", lab),
           mixed(seonin(r), D / "02_선인재단.pdf", lab),
           mixed(songdo(r), D / "03_송도.pdf", lab),
           mixed([(z, h.replace(">사전조사<br>", "><br>")) for z, h in M.gulpo()], D / "05_굴포천.pdf", lab),
           mixed(rodeo(r), D / "06_로데오거리.pdf", lab),
           mixed(terminal(r), D / "07_연안여객터미널.pdf", lab)]
    if r == 1:
        out.append(board_pdf(M.boards_china()[0], D / "04_차이나타운_폼보드.pdf", "BOARDL"))
    else:
        out.append(mixed(china_web(), D / "04_차이나타운_웹기록.pdf", lab))
    out.append(board_pdf(M.board("굴포천", "그림이 있는 이 자리,<br>어떠세요?", "오늘 이용해 보신 그대로, 질문마다 스티커 한 장씩 붙여 주세요.",
                                 [("1", "머물고 싶을 만큼 매력적인가요?"), ("2", "지금 이 공간에 만족하시나요?"),
                                  ("3", "작가 작품이 있는 이 공간, 앞으로가 기대되나요?"), ("4", "다른 다리 밑 공간도 이렇게 바뀌면 이용하고 싶나요?")],
                                 M.YES5, ""), D / "05_굴포천_폼보드.pdf", "BOARD"))
    out.append(board_pdf(M.board("연안여객터미널", "기다리는 이 자리,<br>어떠세요?", "2층 휴식공간을 이용해 보신 그대로, 질문마다 스티커 한 장씩 붙여 주세요.",
                                 [("1", "이 휴식공간 조성에 만족하시나요?"), ("2", "위생적이고 안심하고 쉴 수 있나요?")],
                                 M.YES5, ""), D / "07_연안여객터미널_폼보드.pdf", "BOARD"))
    M._frame = ORIG_FRAME
    M.MAP_DIRS = [C.ROOT / "약산초_지도"]
    return out


if __name__ == "__main__":
    for r in (1, 2):
        for f in build(r):
            print(Path(f).relative_to(BASE))
