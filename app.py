import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# 1. 페이지 레이아웃 및 브라우저 타이틀 설정
st.set_page_config(page_title="불휘논술 성적표 관리 및 자동 백업 시스템", layout="wide")

# 2. '불휘논술' 정체성에 맞춘 프리미엄 테마 및 인쇄 레이아웃 왜곡 차단 CSS
# 화면에서는 양방향 배치가 유지되지만, 인쇄 시에는 왼쪽 입력 컬럼을 화면에서 감추고 성적표만 단독 출력시킵니다.
st.markdown("""
<style>
    body { background-color: #F8FAFC; }
    .report-page {
        background-color: #FFFFFF;
        width: 210mm;
        min-height: 297mm;
        height: auto;
        padding: 20mm;
        margin: 20px auto;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
        box-sizing: border-box;
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        color: #1E293B;
        position: relative;
    }
    .report-title-banner {
        background-color: #0F172A;
        color: #FFFFFF;
        padding: 20px;
        text-align: center;
        border-radius: 6px;
        margin-bottom: 25px;
    }
    .section-title {
        color: #0F172A;
        font-size: 18px;
        font-weight: bold;
        border-left: 5px solid #15803D;
        padding-left: 10px;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .info-table th, .info-table td { border: 1px solid #E2E8F0; padding: 12px; text-align: center; font-size: 14px; }
    .info-table th { background-color: #F1F5F9; color: #334155; }
    .metric-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; }
    .metric-card { flex: 1; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 15px; text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #0F172A; margin-top: 5px; }
    
    @media print {
        /* 1. 불필요한 공통 UI 숨김 */
        [data-testid="stSidebar"], .print-exclude, header, footer, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        
        /* 2. [핵심] 인쇄 시 왼쪽 입력 컬럼을 숨기고 오른쪽 성적표 컬럼만 100% 가로폭으로 조정 */
        div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
            display: none !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
        
        /* 3. A4 규격 출력 제어 (높이를 auto와 min-height로 처리하여 빈 페이지 여백 초과 방지) */
        .report-page {
            border: none !important;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 15mm !important;
            width: 100% !important;
            min-height: 297mm !important;
            height: auto !important;
            page-break-after: always !important;
            break-before: page !important;
            break-after: page !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 🌟 영구 백업용 엑셀 파일 경로 지정
EXCEL_FILE_PATH = "nonsul_total_backup.xlsx"

# 3. 데이터베이스 시스템 기동 (복구 안정성 강화형)
# 수동 엑셀 편집 도중 비어 있는 셀(Null)이 들어가더라도 자료 파싱이 중단되지 않고 유연하게 복구되도록 예외 보호 장치를 추가했습니다.
if "db" not in st.session_state:
    if os.path.exists(EXCEL_FILE_PATH):
        try:
            df_load = pd.read_excel(EXCEL_FILE_PATH)
            loaded_db = []
            
            # 셀 값 안전 파싱용 내부 도우미 함수
            def safe_val(row, col, default_val, is_int=False):
                val = row.get(col)
                if pd.isna(val) or val is None:
                    return default_val
                return int(val) if is_int else val

            for _, row in df_load.iterrows():
                loaded_db.append({
                    "student_name": safe_val(row, "학생 이름", "미지정"),
                    "class_name": safe_val(row, "수강 반", "기본 반"),
                    "week": safe_val(row, "회차", "기본 회차"),
                    "essay_type": safe_val(row, "논술 유형", "요약형"),
                    "instructor": safe_val(row, "강사", "불휘교사"),
                    "reg_task_name": safe_val(row, "정규 문항명", "정규 문제"),
                    "reg_total": safe_val(row, "정규 총점", 0, is_int=True),
                    "reg_scores": {
                        "이해력": safe_val(row, "정규_이해", 0, is_int=True),
                        "분석력": safe_val(row, "정규_분석", 0, is_int=True),
                        "논증력": safe_val(row, "정규_논증", 0, is_int=True),
                        "창의력": safe_val(row, "정규_창의", 0, is_int=True),
                        "표현력": safe_val(row, "정규_표현", 0, is_int=True)
                    },
                    "reg_comments": {
                        "reading": safe_val(row, "정규_독해코멘트", ""),
                        "topic": safe_val(row, "정규_논점코멘트", ""),
                        "concept": safe_val(row, "정규_배경코멘트", ""),
                        "other": safe_val(row, "정규_기타코멘트", "")
                    },
                    "supp_task_name": safe_val(row, "보충 문항명", "보충 문제"),
                    "supp_total": safe_val(row, "보충 총점", 0, is_int=True),
                    "supp_scores": {
                        "이해력": safe_val(row, "보충_이해", 0, is_int=True),
                        "분석력": safe_val(row, "보충_분석", 0, is_int=True),
                        "논증력": safe_val(row, "보충_논증", 0, is_int=True),
                        "창의력": safe_val(row, "보충_창의", 0, is_int=True),
                        "표현력": safe_val(row, "보충_표현", 0, is_int=True)
                    },
                    "supp_comments": {
                        "reading": safe_val(row, "보충_독해코멘트", ""),
                        "topic": safe_val(row, "보충_논점코멘트", ""),
                        "concept": safe_val(row, "보충_배경코멘트", ""),
                        "other": safe_val(row, "보충_기타코멘트", "")
                    },
                    "overall_guide": safe_val(row, "종합 가이드", ""),
                    "rank": safe_val(row, "반 석차", 1, is_int=True),
                    "total_students": safe_val(row, "반 정원", 1, is_int=True)
                })
            st.session_state.db = loaded_db
        except Exception as e:
            st.session_state.db = []
    else:
        st.session_state.db = []

def generate_html_table(scores, total):
    rows = "".join([f"<tr><td style='font-weight:bold; background-color:#F8FAFC;'>{k}</td><td style='color:#0F172A; font-weight:bold;'>{v}</td><td>20</td></tr>" for k, v in scores.items()])
    return f'<table class="info-table"><thead><tr><th>평가 영역</th><th>획득 점수</th><th>만점</th></tr></thead><tbody>{rows}<tr style="background-color:#F0FDF4; font-weight:bold;"><td>합계 점수</td><td style="color:#15803D; font-size:16px;">{total}</td><td>100</td></tr></tbody></table>'

categories = ["이해력", "분석력", "논증력", "창의력", "표현력"]

# 화면 분할
col_in, col_out = st.columns([1, 2])

# ==================== [LEFT: 강사 성적 입력 관리 기능] ====================
with col_in:
    st.markdown("### 🌿 불휘논술 성적 입력 콘솔")
    
    with st.expander("1. 학생 및 회차 기본 정보", expanded=True):
        in_name = st.text_input("학생 이름", "홍길동")
        in_class = st.text_input("수강 반", "명문대 전형 수시반")
        in_week = st.text_input("해당 주차 정보", "정규 23회차")
        in_type = st.selectbox("🌟 논술 문항 유형", ["요약형", "비교형", "비판/평가형", "대안제시형", "도표/통계분석형"], index=1)
        in_rank = st.number_input("반 석차 (등)", min_value=1, value=3)
        in_total_students = st.number_input("반 정원 (명)", min_value=1, value=20)
        in_instructor = st.text_input("담당 강사 성명", "불휘교사")
        
    with st.expander("2. 📘 [정규 문항] 점수 및 코멘트", expanded=False):
        in_reg_name = st.text_input("정규 문제명", "2019 가톨릭대 수시")
        r_scores = {cat: st.slider(f"정규-{cat}", 0, 20, 16) for cat in categories}
        r_total = sum(r_scores.values())
        r_comments = {
            "reading": st.text_area("정규-독해 코멘트", "글의 대조적 구도를 파악하는 이해가 안정적임."),
            "topic": st.text_area("정규-출제논점 코멘트", "제시문 속에 감춰진 전제를 다차원적으로 파고듦."),
            "concept": st.text_area("정규-배경지식 코멘트", "논제와 관련된 핵심 이론을 적정 수준에서 비틀어 지적함."),
            "other": st.text_area("정규-기타 코멘트", "문장의 결말과 주술 호응이 상당히 개선됨.")
        }
        
    with st.expander("3. 📙 [보충 문항] 점수 및 코멘트", expanded=False):
        in_supp_name = st.text_input("보충 문제명", "비교 응용 및 추론 클리닉")
        s_scores = {cat: st.slider(f"보충-{cat}", 0, 20, 15) for cat in categories}
        s_total = sum(s_scores.values())
        s_comments = {
            "reading": st.text_area("보충-독해 코멘트", "기초 사상의 주요 갈래를 빈틈없이 명료화함."),
            "topic": st.text_area("보충-출제논점 코멘트", "제시문의 세부 지엽적 개념을 가볍게 축소 해석함."),
            "concept": st.text_area("보충-배경지식 코멘트", "주장 설계에 필수 이론을 잘 용해시켜 녹임."),
            "other": st.text_area("보충-기타 코멘트", "맞춤법 및 문장 구획 나누기가 올바름.")
        }
        
    in_guide = st.text_area("🧭 주차별 평가 종합 지도 제안", "주제 파악 및 독해 분석 능력이 매우 뛰어납니다. 뿌리가 단단하게 잡혀 있으니, 서론에서 결론으로 이행하는 논증 과정의 결속성 향상에 더욱 집중해 나간다면 더 큰 성취가 기대됩니다.")

    st.markdown("---")
    # 🌟 [영구 백업 및 수정용 핵심 버튼]
    if st.button("💾 현재 성적표 엑셀 파일에 영구 저장하기", type="primary", use_container_width=True):
        new_record = {
            "student_name": in_name, "class_name": in_class, "week": in_week, "essay_type": in_type, "instructor": in_instructor,
            "reg_task_name": in_reg_name, "reg_total": r_total, "reg_scores": r_scores, "reg_comments": r_comments,
            "supp_task_name": in_supp_name, "supp_total": s_total, "supp_scores": s_scores, "supp_comments": s_comments,
            "overall_guide": in_guide, "rank": in_rank, "total_students": in_total_students
        }
        
        duplicate_idx = next((i for i, item in enumerate(st.session_state.db) if item["student_name"] == in_name and item["week"] == in_week), None)
        if duplicate_idx is not None:
            st.session_state.db[duplicate_idx] = new_record
        else:
            st.session_state.db.append(new_record)
            
        excel_flat = []
        for x in st.session_state.db:
            excel_flat.append({
                "학생 이름": x["student_name"], "수강 반": x["class_name"], "회차": x["week"], "논술 유형": x["essay_type"], "반 석차": x["rank"], "반 정원": x["total_students"], "강사": x["instructor"],
                "정규 문항명": x["reg_task_name"], "정규 총점": x["reg_total"], "정규_이해": x["reg_scores"]["이해력"], "정규_분석": x["reg_scores"]["분석력"], "정규_논증": x["reg_scores"]["논증력"], "정규_창의": x["reg_scores"]["창의력"], "정규_표현": x["reg_scores"]["표현력"],
                "정규_독해코멘트": x["reg_comments"]["reading"], "정규_논점코멘트": x["reg_comments"]["topic"], "정규_배경코멘트": x["reg_comments"]["concept"], "정규_기타코멘트": x["reg_comments"]["other"],
                "보충 문항명": x["supp_task_name"], "보충 총점": x["supp_total"], "보충_이해": x["supp_scores"]["이해력"], "보충_분석": x["supp_scores"]["분석력"], "보충_논증": x["supp_scores"]["논증력"], "보충_창의": x["supp_scores"]["창의력"], "보충_표현": x["supp_scores"]["표현력"],
                "보충_독해코멘트": x["supp_comments"]["reading"], "보충_논점코멘트": x["supp_comments"]["topic"], "보충_배경코멘트": x["supp_comments"]["concept"], "보충_기타코멘트": x["supp_comments"]["other"],
                "종합 가이드": x["overall_guide"]
            })
        
        df_excel = pd.DataFrame(excel_flat)
        df_excel.to_excel(EXCEL_FILE_PATH, index=False)
        st.success(f"✅ {in_name} 학생의 {in_week} 데이터가 누적 연동되어 '{EXCEL_FILE_PATH}' 파일에 자동 영구 백업되었습니다!")

# ==================== [RIGHT: 3장 완결형 프리미엄 성적표 출력 뷰] ====================
with col_out:
    st.markdown("<div class='print-exclude'><h3>🖨️ 성적표 실시간 프리뷰</h3><p>입력이 완료되면 왼쪽 하단의 <b>엑셀 영구 저장 버튼</b>을 누르고, 키보드에서 <b>Ctrl + P</b>를 눌러 PDF로 인쇄하세요.</p></div>", unsafe_allow_html=True)

    # ---------------- [PAGE 1: 성적표 표지 및 요약] ----------------
    st.markdown('<div class="report-page">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #0F172A; padding-bottom: 8px; margin-bottom: 50px;">
        <span style="font-size: 13px; color: #15803D; font-weight: bold;">[뿌리깊은 대입논술] 불휘논술아카데미</span>
        <span style="font-size: 13px; color: #64748B;">STUDENT PERFORMANCE REPORT</span>
    </div>
    
    <div style="text-align: center; margin-top: 60px; margin-bottom: 60px;">
        <h1 style="color: #0F172A; font-size: 34px; margin-bottom: 15px; letter-spacing: 2px;">주차별 논술고사 분석 리포트</h1>
        <p style="color: #475569; font-size: 14px;">본 리포트는 단순한 점수 산출을 넘어 수강생의 논리적 독해 뿌리와 표현 역량을 정밀 진단합니다.</p>
    </div>
    
    <table class="info-table" style="margin-bottom: 50px;">
        <tr><th style="width:25%;">평가 수강생</th><td style="width:25%;"><b>{in_name}</b> 학생</td><th style="width:25%;">담당 클래스</th><td style="width:25%;">{in_class}</td></tr>
        <tr><th>평가 회차</th><td>{in_week}</td><th>문항 핵심 유형</th><td><span style="background-color: #F0FDF4; color: #166534; padding: 3px 8px; border-radius: 4px; font-weight: bold;">{in_type}</span></td></tr>
    </table>
    
    <div class="section-title">📊 이번 주 종합 평가 결과 요약</div>
    <div class="metric-container">
        <div class="metric-card"><div style="font-size: 13px; color: #64748B;">정규 문항 총점</div><div class="metric-value" style="color: #0F172A;">{r_total} <span style="font-size: 14px; color: #94A3B8;">/ 100</span></div></div>
        <div class="metric-card"><div style="font-size: 13px; color: #64748B;">보충 문항 총점</div><div class="metric-value" style="color: #15803D;">{s_total} <span style="font-size: 14px; color: #94A3B8;">/ 100</span></div></div>
        <div class="metric-card"><div style="font-size: 13px; color: #64748B;">현재 반 석차</div><div class="metric-value">{in_rank} <span style="font-size: 14px; color: #94A3B8;">/ {in_total_students} 명</span></div></div>
    </div>
    
    <div style="position: absolute; bottom: 20mm; left: 20mm; right: 20mm; text-align: center; color: #94A3B8; font-size: 12px; border-top: 1px solid #E2E8F0; padding-top: 15px;">
        불휘논술연구소 | Page 1
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- [PAGE 2: 정규 문항 상세 진단] ----------------
    st.markdown('<div class="report-page">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="report-title-banner">
        <h3 style="margin: 0; font-size: 17px; letter-spacing:0.5px;">I. 정규 평가 입체 정밀 진단</h3>
    </div>
    <p style="font-size: 13.5px; color: #475569; margin-bottom: 20px;">
        실전 대입 기출 문항인 <b>[{in_reg_name}]</b>에 대한 학생의 영역별 성취도 분석 결과입니다.
    </p>
    """, unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns([1.1, 1.2])
    with col_r1:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        st.markdown(generate_html_table(r_scores, r_total), unsafe_allow_html=True)
    with col_r2:
        fig_r = go.Figure(go.Scatterpolar(
            r=list(r_scores.values()) + [list(r_scores.values())[0]],
            theta=categories + [categories[0]],
            fill='toself', line_color='#0F172A', fillcolor='rgba(15, 23, 42, 0.12)'
        ))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20], tickfont=dict(size=9))), height=240, margin=dict(l=45, r=45, t=15, b=15), showlegend=False)
        st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown('<div class="section-title">✏️ 채점관 세부 항목별 정밀 진단 의견</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div style="background-color: #F8FAFC; border-left: 4px solid #0F172A; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #0F172A; margin-bottom: 5px; font-size: 13.5px;">📖 독해 분석 역량</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{r_comments['reading']}</div>
        </div>
        <div style="background-color: #F8FAFC; border-left: 4px solid #0F172A; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #0F172A; margin-bottom: 5px; font-size: 13.5px;">🎯 출제논점 전제 파악</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{r_comments['topic']}</div>
        </div>
        <div style="background-color: #F8FAFC; border-left: 4px solid #0F172A; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #0F172A; margin-bottom: 5px; font-size: 13.5px;">💡 배경이론 및 정합성</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{r_comments['concept']}</div>
        </div>
        <div style="background-color: #F8FAFC; border-left: 4px solid #0F172A; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #0F172A; margin-bottom: 5px; font-size: 13.5px;">✍ 문장 표현 및 원고지 기술</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{r_comments['other']}</div>
        </div>
    </div>
    
    <div style="position: absolute; bottom: 20mm; left: 20mm; right: 20mm; text-align: center; color: #94A3B8; font-size: 12px; border-top: 1px solid #E2E8F0; padding-top: 15px;">
        불휘논술연구소 | Page 2
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- [PAGE 3: 보충 문항 및 종합 가이드] ----------------
    st.markdown('<div class="report-page">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="report-title-banner" style="background-color: #15803D;">
        <h3 style="margin: 0; font-size: 17px; letter-spacing:0.5px;">II. 보충 클리닉 및 종합 처방 지침</h3>
    </div>
    <p style="font-size: 13.5px; color: #475569; margin-bottom: 20px;">
        단원별 약점 보완 및 기초 역량 강화를 위한 보충 문항 <b>[{in_supp_name}]</b> 평가 결과입니다.
    </p>
    """, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([1.1, 1.2])
    with col_s1:
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        st.markdown(generate_html_table(s_scores, s_total), unsafe_allow_html=True)
    with col_s2:
        fig_s = go.Figure(go.Scatterpolar(
            r=list(s_scores.values()) + [list(s_scores.values())[0]],
            theta=categories + [categories[0]],
            fill='toself', line_color='#15803D', fillcolor='rgba(21, 128, 61, 0.12)'
        ))
        fig_s.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20], tickfont=dict(size=9))), height=240, margin=dict(l=45, r=45, t=15, b=15), showlegend=False)
        st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown('<div class="section-title">✏️ 보충 문항 클리닉 진단 의견</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
        <div style="background-color: #F8FAFC; border-left: 4px solid #15803D; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #15803D; margin-bottom: 5px; font-size: 13.5px;">📖 독해 분석 역량</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{s_comments['reading']}</div>
        </div>
        <div style="background-color: #F8FAFC; border-left: 4px solid #15803D; padding: 12px; border-radius: 4px;">
            <div style="font-weight: bold; color: #15803D; margin-bottom: 5px; font-size: 13.5px;">🎯 출제논점 전제 파악</div>
            <div style="color: #475569; font-size: 12.5px; line-height: 1.5;">{s_comments['topic']}</div>
        </div>
    </div>
    
    <div class="section-title">주차별 성취도 평가 종합 지도 의견</div>
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 18px; border-radius: 6px; font-size: 13.5px; line-height: 1.6; color: #334155;">
        {in_guide}
    </div>
    
    <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 50px; font-size: 14px;">
        <span style="color: #475569; margin-right: 15px;">평가 주관 강사 :</span>
        <span style="font-weight: bold; border-bottom: 1px solid #334155; padding-bottom: 2px; width: 100px; text-align: center; color: #0F172A;">{in_instructor}</span>
        <span style="color: #475569; margin-left: 10px;">(인)</span>
    </div>
    
    <div style="position: absolute; bottom: 20mm; left: 20mm; right: 20mm; text-align: center; color: #94A3B8; font-size: 12px; border-top: 1px solid #E2E8F0; padding-top: 15px;">
        불휘논술연구소 | Page 3
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)