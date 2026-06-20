import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="바른지성 논술 성적 관리 시스템", layout="wide")

# 2. 고급스러운 Navy/Slate Gray 테마 및 모바일/인쇄 최적화 하이브리드 CSS
st.markdown("""
<style>
    body { background-color: #F8FAFC; }
    .report-page {
        background-color: #FFFFFF;
        max-width: 850px;
        margin: 20px auto;
        padding: 35px;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05);
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        color: #1E293B;
    }
    .report-title-banner {
        background-color: #1B365D;
        color: #FFFFFF;
        padding: 18px;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .section-title {
        color: #1B365D;
        font-size: 17px;
        font-weight: bold;
        border-left: 5px solid #1B365D;
        padding-left: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .info-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .info-table th, .info-table td { border: 1px solid #E2E8F0; padding: 10px; text-align: center; font-size: 13px; }
    .info-table th { background-color: #F1F5F9; color: #334155; }
    .metric-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 20px; }
    .metric-card { flex: 1; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; text-align: center; }
    .metric-value { font-size: 22px; font-weight: bold; color: #1B365D; margin-top: 5px; }
    
    @media print {
        [data-testid="stSidebar"], header, footer, .stDeployButton, [data-testid="stToolbar"], [data-testid="stDecoration"], .stTabs, .print-exclude, .stAlert {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        .report-page { border: none !important; box-shadow: none !important; margin: 0 !important; padding: 10mm !important; width: 100% !important; page-break-after: always !important; break-after: page !important; }
    }
</style>
""", unsafe_allow_html=True)

# 3. 임시 데이터베이스 기동 및 샘플(Mock) 데이터 적재
if "db" not in st.session_state:
    st.session_state.db = [
        {
            "student_name": "홍길동", "student_phone": "1234", "class_name": "명문대 수시 집중반", "week": "정규 21회차", "essay_type": "비교형", "instructor": "김논술",
            "reg_task_name": "2018 연세대 정규", "reg_scores": {"이해력": 14, "분석력": 15, "논증력": 13, "창의력": 12, "표현력": 14}, "reg_total": 68, "class_avg": 70.5,
            "reg_comments": {"reading": "핵심 논점은 짚었으나 서술의 깊이가 다소 평이함.", "topic": "공통 기준점을 2개 이상 도출하려 애쓴 점이 돋보임.", "concept": "현대 정의론 관점을 원용하려 했으나 맥락이 모호함.", "other": "문장의 종결어미가 반복되는 경향이 있음."},
            "supp_task_name": "비교 요약 보충", "supp_scores": {"이해력": 13, "분석력": 14, "논증력": 12, "창의력": 11, "표현력": 14}, "supp_total": 64,
            "supp_comments": {"reading": "요약 한계 분량 400자를 비교적 양호하게 준수함.", "topic": "제시문 다의 핵심 키워드를 일부분 누락함.", "concept": "기본적인 분석 도구 활용 능력이 무난한 편임.", "other": "글씨 가독성이 개선될 필요가 있음."},
            "overall_guide": "비교 논증의 설계 틀은 잘 잡혀 있으나 문장의 밀도와 완성도를 더 보완해야 합니다."
        },
        {
            "student_name": "홍길동", "student_phone": "1234", "class_name": "명문대 수시 집중반", "week": "정규 22회차", "essay_type": "비교형", "instructor": "김논술",
            "reg_task_name": "2019 고려대 정규", "reg_scores": {"이해력": 16, "분석력": 16, "논증력": 15, "창의력": 13, "표현력": 15}, "reg_total": 75, "class_avg": 72.1,
            "reg_comments": {"reading": "제시문 간의 질적 차이를 지난 주 대비 정밀하게 독해함.", "topic": "출제자가 요구한 입장의 스펙트럼 분석을 성실히 이행함.", "concept": "자유와 평등의 상충 개념을 적극 서술해 논리를 더함.", "other": "주요 핵심 어휘의 어휘력이 매우 성숙해졌음."},
            "supp_task_name": "비교 응용 심화", "supp_scores": {"이해력": 15, "분석력": 15, "논증력": 14, "창의력": 12, "표현력": 15}, "supp_total": 71,
            "supp_comments": {"reading": "보충 텍스트의 구조적 갈등 지점을 완전히 파악함.", "topic": "대립하는 가치론의 성격을 명확히 기술함.", "concept": "배경지식이 본인의 주장 뒷받침에 잘 정착됨.", "other": "전반적인 어조의 일관성이 높게 유지됨."},
            "overall_guide": "비교형 문항에 대한 이해도가 상당히 향상되어 높은 성취를 이루었습니다."
        }
    ]

def generate_html_table(scores, total):
    rows = "".join([f"<tr><td style='font-weight:bold; background-color:#F8FAFC;'>{k}</td><td style='color:#1B365D; font-weight:bold;'>{v}</td><td>20</td></tr>" for k, v in scores.items()])
    return f'<table class="info-table"><thead><tr><th>평가 영역</th><th>내 점수</th><th>만점</th></tr></thead><tbody>{rows}<tr style="background-color:#EFF6FF; font-weight:bold;"><td>합계 점수</td><td style="color:#1B365D; font-size:16px;">{total}</td><td>100</td></tr></tbody></table>'

# ==================== 메인 시스템 사이드바 ====================
st.sidebar.title("🏛 바른지성 논술")
user_mode = st.sidebar.radio("접속 권한 선택", ["👨‍👩‍👦 학부모/학생 전용 조회", "🔒 학원 강사 관리 모드"])

# ==================== [MODE 1: 학부모/학생 전용 조회 화면] ====================
if user_mode == "👨‍👩‍👦 학부모/학생 전용 조회":
    st.title("🏛 바른지성 논술아카데미 성적 조회 시스템")
    
    st.markdown("""
    <div class="print-exclude" style="background-color: #EFF6FF; border-left: 4px solid #1E40AF; padding: 12px; margin-bottom: 15px; border-radius: 6px; font-size: 13px; color: #1E3A8A;">
        💡 <b>성적표 PDF 저장/출력 팁:</b> 브라우저에서 <b>Ctrl + P (Mac은 Cmd + P)</b>를 누르시면 성적 리포트만 A4 규격으로 인쇄하거나 PDF로 저장할 수 있습니다. (인쇄 설정 시 '배경 그래픽'을 꼭 체크해 주세요.)
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_name = st.text_input("🔍 수강생 이름 입력", placeholder="예: 홍길동").strip()
    with col_s2:
        search_phone = st.text_input("📱 전화번호 뒷 4자리 입력", placeholder="예: 1234", type="password").strip()
    
    if search_name and search_phone:
        df_db = pd.DataFrame(st.session_state.db)
        df_student = df_db[(df_db["student_name"] == search_name) & (df_db["student_phone"] == search_phone)] if len(df_db) > 0 else pd.DataFrame()
        
        if len(df_student) > 0:
            p_tab1, p_tab2 = st.tabs(["✍ 주차별 최신 성적표", "📊 단원 유형별 종합 분석"])
            
            with p_tab1:
                available_weeks = sorted(df_student["week"].unique(), reverse=True)
                selected_week = st.selectbox("조회할 회차(주차) 선택", available_weeks)
                report_data = df_student[df_student["week"] == selected_week].iloc[0]
                
                st.markdown('<div class="report-page">', unsafe_allow_html=True)
                st.markdown(f'<div class="report-title-banner"><h2>주차별 논술고사 분석 리포트 ({selected_week})</h2></div>', unsafe_allow_html=True)
                st.markdown(f"""
                <table class="info-table">
                    <tr><th>수강생</th><td><b>{report_data['student_name']}</b> 학생</td><th>담당 클래스</th><td>{report_data['class_name']}</td></tr>
                    <tr><th>평가 회차</th><td>{report_data['week']}</td><th>문항 핵심 유형</th><td><b>{report_data['essay_type']}</b></td></tr>
                </table>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-card"><div>정규 총점</div><div class="metric-value">{report_data["reg_total"]}점</div></div>
                    <div class="metric-card"><div>보충 총점</div><div class="metric-value">{report_data["supp_total"]}점</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                # 정규 세부 지표
                st.markdown(f"<div class='section-title'>📘 정규 문항 분석: [{report_data['reg_task_name']}]</div>", unsafe_allow_html=True)
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown(generate_html_table(report_data['reg_scores'], report_data['reg_total']), unsafe_allow_html=True)
                with col_r2:
                    categories = list(report_data['reg_scores'].keys())
                    fig = go.Figure(go.Scatterpolar(
                        r=list(report_data['reg_scores'].values())+[list(report_data['reg_scores'].values())[0]], 
                        theta=categories+[categories[0]], fill='toself', line_color='#1B365D', fillcolor='rgba(27, 54, 93, 0.2)'
                    ))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20], tickfont=dict(size=9))), height=220, margin=dict(l=40,r=40,t=15,b=15))
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                st.markdown(f"""
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:20px;">
                    <div style="background:#F8FAFC; border-left:4px solid #1B365D; padding:10px; font-size:13px; border-radius:4px;"><b>📖 독해 분석:</b> {report_data['reg_comments']['reading']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #1B365D; padding:10px; font-size:13px; border-radius:4px;"><b>🎯 출제논점:</b> {report_data['reg_comments']['topic']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #1B365D; padding:10px; font-size:13px; border-radius:4px;"><b>💡 배경이론:</b> {report_data['reg_comments']['concept']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #1B365D; padding:10px; font-size:13px; border-radius:4px;"><b>✍ 표현 기술:</b> {report_data['reg_comments']['other']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 보충 세부 지표
                st.markdown(f"<div class='section-title'>📙 보충 문항 분석: [{report_data['supp_task_name']}]</div>", unsafe_allow_html=True)
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown(generate_html_table(report_data['supp_scores'], report_data['supp_total']), unsafe_allow_html=True)
                with col_s2:
                    categories_supp = list(report_data['supp_scores'].keys())
                    fig2 = go.Figure(go.Scatterpolar(
                        r=list(report_data['supp_scores'].values())+[list(report_data['supp_scores'].values())[0]], 
                        theta=categories_supp+[categories_supp[0]], fill='toself', line_color='#0284C7', fillcolor='rgba(2, 132, 199, 0.15)'
                    ))
                    fig2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20], tickfont=dict(size=9))), height=220, margin=dict(l=40,r=40,t=15,b=15))
                    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                
                st.markdown(f"""
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:20px;">
                    <div style="background:#F8FAFC; border-left:4px solid #0284C7; padding:10px; font-size:13px; border-radius:4px;"><b>📖 독해 분석:</b> {report_data['supp_comments']['reading']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #0284C7; padding:10px; font-size:13px; border-radius:4px;"><b>🎯 출제논점:</b> {report_data['supp_comments']['topic']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #0284C7; padding:10px; font-size:13px; border-radius:4px;"><b>💡 배경이론:</b> {report_data['supp_comments']['concept']}</div>
                    <div style="background:#F8FAFC; border-left:4px solid #0284C7; padding:10px; font-size:13px; border-radius:4px;"><b>✍ 표현 기술:</b> {report_data['supp_comments']['other']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div class='section-title'>🧭 주차별 평가 종합 지도 의견</div><div style='background:#F8FAFC; padding:15px; border-radius:6px; font-size:13.5px; line-height:1.6; border:1px solid #E2E8F0;'>{report_data['overall_guide']}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:right; margin-top:25px; font-size:14px; font-weight:bold;'>담당 평가 강사: {report_data['instructor']} (인)</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with p_tab2:
                selected_type = st.selectbox("종합 분석할 논술 문항 유형 선택", ["요약형", "비교형", "비판/평가형", "대안제시형", "도표/통계분석형"], index=1)
                df_filtered = df_student[df_student["essay_type"] == selected_type]
                
                if len(df_filtered) > 0:
                    st.markdown(f"### 📊 [{selected_type}] 유형 통합 성취 리포트")
                    
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.markdown("<p style='font-weight:bold; color:#1B365D; margin-bottom:5px;'>📈 회차별 총점 발달 추이 (반 평균 대조선 포함)</p>", unsafe_allow_html=True)
                        
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(x=df_filtered["week"], y=df_filtered["reg_total"], mode='lines+markers', name='내 정규 점수', line=dict(color='#1B365D', width=3)))
                        fig_trend.add_trace(go.Scatter(x=df_filtered["week"], y=df_filtered["class_avg"], mode='lines+markers', name='반 평균', line=dict(color='#94A3B8', dash='dash')))
                        fig_trend.update_layout(yaxis=dict(range=[40, 105], title="점수"), xaxis=dict(title="회차"), margin=dict(l=10, r=10, t=10, b=10), height=250, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
                        st.plotly_chart(fig_trend, use_container_width=True)
                    with col_c2:
                        st.markdown("<p style='font-weight:bold; color:#1B365D; margin-bottom:5px;'>🎯 대단원 누적 평균 역량 방사형 차트</p>", unsafe_allow_html=True)
                        acc_scores = {k: round(df_filtered["reg_scores"].apply(lambda x: x[k]).mean(), 1) for k in report_data['reg_scores'].keys()}
                        acc_cats = list(acc_scores.keys())
                        fig_radar_acc = go.Figure(go.Scatterpolar(r=list(acc_scores.values())+[list(acc_scores.values())[0]], theta=acc_cats+[acc_cats[0]], fill='toself', line_color='#10B981', fillcolor='rgba(16, 185, 129, 0.15)'))
                        fig_radar_acc.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20], tickfont=dict(size=9))), height=250, margin=dict(l=40, r=40, t=15, b=15))
                        st.plotly_chart(fig_radar_acc, use_container_width=True)
                else:
                    st.info(f"💡 {search_name} 학생은 아직 [{selected_type}] 단원의 누적 데이터가 존재하지 않습니다.")
        else:
            st.error("❌ 등록된 수강생 정보가 없거나 인증 번호가 일치하지 않습니다.")

# ==================== [MODE 2: 학원 강사 관리 모드 화면] ====================
elif user_mode == "🔒 학원 강사 관리 모드":
    st.title("🔒 학원 강사 전용 성적 관리 시스템")
    password = st.text_input("강사 전용 인증 보안 코드를 입력하세요", type="password")
    
    if password == "1234":
        st.success("🔓 강사 인증에 성공했습니다.")
        tab1, tab2 = st.tabs(["✍ 신규 성적 입력", "🗄 전체 데이터베이스 원장 관리"])
        
        with tab1:
            st.subheader("📝 학생별 주차 성적 수동 입력")
            c1, c2 = st.columns(2)
            with c1:
                in_name = st.text_input("학생 이름", "홍길동")
                in_class = st.text_input("수강 반", "명문대 수시 집중반")
                in_phone = st.text_input("📱 학부모 인증용 전화번호 뒷 4자리", "1234")
            with c2:
                in_week = st.text_input("해당 주차 정보", "정규 23회차")
                in_type = st.selectbox("🌟 논술 문항 유형 선택", ["요약형", "비교형", "비판/평가형", "대안제시형", "도표/통계분석형"], index=1)
                in_class_avg = st.number_input("📊 해당 주차 반 평균 총점", min_value=0, max_value=100, value=72)
            
            in_instructor = st.text_input("담당 강사 성명", "김논술")
            
            st.markdown("---")
            col_reg, col_supp = st.columns(2)
            
            with col_reg:
                st.markdown("### 📘 [정규 문항] 점수 및 코멘트")
                in_reg_name = st.text_input("정규 문제명", "2020 연세대 수시 정규")
                r_scores = {cat: st.slider(f"정규-{cat}", 0, 20, 15) for cat in ["이해력", "분석력", "논증력", "창의력", "표현력"]}
                r_comments = {
                    "reading": st.text_input("정규-독해 코멘트", "글의 대조적 구도를 파악하는 이해가 안정적임."),
                    "topic": st.text_input("정규-출제논점 코멘트", "제시문 속에 감춰진 전제를 다차원적으로 파고듦."),
                    "concept": st.text_input("정규-배경지식 코멘트", "자유론적 가치의 한계를 적정 수준에서 비틀어 지적함."),
                    "other": st.text_input("정규-기타 코멘트", "문장의 결말 och 주술 호응이 상당히 개선됨.")
                }
                
            with col_supp:
                st.markdown("### 📙 [보충 문항] 점수 및 코멘트")
                in_supp_name = st.text_input("보충 문제명", "요약 기법 및 추론 보충")
                s_scores = {cat: st.slider(f"보충-{cat}", 0, 20, 14) for cat in ["이해력", "분석력", "논증력", "창의력", "표현력"]}
                s_comments = {
                    "reading": st.text_input("보충-독해 코멘트", "기초 사상의 주요 갈래를 빈틈없이 명료화함."),
                    "topic": st.text_input("보충-출제논점 코멘트", "제시문의 세부 지엽적 개념을 가볍게 축소 해석함."),
                    "concept": st.text_input("보충-배경지식 코멘트", "주장 설계에 필수 이론을 잘 용해시켜 녹임."),
                    "other": st.text_input("보충-기타 코멘트", "맞춤법 및 문장 구획 나누기가 올바름.")
                }
            
            in_guide = st.text_area("🧭 강사 종합 가이드 및 처방 지침", "주제 파악 능력이 우수합니다. 본론 서술 시 인과 관계 결속성에 조금 더 집중합시다.")
            
            if st.button("💾 현재 주차 성적 DB에 최종 저장하기", use_container_width=True):
                new_record = {
                    "student_name": in_name, "student_phone": in_phone, "class_name": in_class, "week": in_week, "essay_type": in_type, "instructor": in_instructor,
                    "reg_task_name": in_reg_name, "reg_scores": r_scores, "reg_total": sum(r_scores.values()), "class_avg": in_class_avg, "reg_comments": r_comments,
                    "supp_task_name": in_supp_name, "supp_scores": s_scores, "supp_total": sum(s_scores.values()), "supp_comments": s_comments,
                    "overall_guide": in_guide
                }
                
                duplicate_idx = next((i for i, item in enumerate(st.session_state.db) if item["student_name"] == in_name and item["week"] == in_week), None)
                if duplicate_idx is not None:
                    st.session_state.db[duplicate_idx] = new_record
                    st.success(f"⚠️ 기존 {in_name} 학생의 {in_week} 데이터가 업데이트되었습니다.")
                else:
                    st.session_state.db.append(new_record)
                    st.success(f"✅ {in_name} 학생의 {in_week} 신규 성적이 저장되었습니다.")
                    
        with tab2:
            st.subheader("🗄 원정 데이터베이스")
            if len(st.session_state.db) > 0:
                df_view = pd.DataFrame([{
                    "학생 이름": x["student_name"], "인증번호": x["student_phone"], "클래스": x["class_name"], "회차": x["week"], "단원 유형": x["essay_type"],
                    "정규 총점": x["reg_total"], "반 평균": x["class_avg"], "보충 총점": x["supp_total"], "강사": x["instructor"]
                } for x in st.session_state.db])
                st.dataframe(df_view, use_container_width=True)
                
                csv_data = df_view.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📥 전체 성적 데이터 백업 다운로드 (CSV)", data=csv_data, file_name="nonsul_db.csv", mime="text/csv", use_container_width=True)
                
                if st.button("🚨 원장 전체 초기화", type="primary"):
                    st.session_state.db = []
                    st.rerun()