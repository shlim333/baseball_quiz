import streamlit as st
import pandas as pd

# 설정
st.set_page_config(page_title="KBO 야구 퀴즈 앱", page_icon="⚾")

# 초기 화면
st.title("⚾ KBO & 야구 규칙 마스터 퀴즈")
st.subheader("학번: 2025205003")
st.subheader("이름: 임수현")
st.write("오픈소스소프트웨어실습 중간고사 대체 과제용 야구 퀴즈입니다.")
st.markdown("---")

# 캐싱 사용
@st.cache_data
def load_quiz_data():
    df = pd.read_csv("data/quiz.csv")
    return df

quiz_df = load_quiz_data()

# 세션 초기화
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_idx' not in st.session_state:
    st.session_state['current_idx'] = 0
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'quiz_finished' not in st.session_state:
    st.session_state['quiz_finished'] = False

# 로그인
if not st.session_state['logged_in']: 
    st.write("### 타격장 입장 (로그인)")
    with st.form("login_form"):
        st.info("입장을 위해 아이디(학번)와 비밀번호(1234)를 입력해주세요.")
        user_id = st.text_input("아이디 (학번)")
        user_pw = st.text_input("비밀번호", type="password")
        team = st.selectbox("응원하는 구단을 선택하세요", 
                            ["LG 트윈스", "KT 위즈", "SSG 랜더스", "NC 다이노스", "두산 베어스", 
                             "KIA 타이거즈", "롯데 자이언츠", "삼성 라이온즈", "한화 이글스", "키움 히어로즈"])
        submit_button = st.form_submit_button("입장하기")

        if submit_button:
            if user_id == "2025205003" and user_pw == "1234":
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                st.session_state['team'] = team
                st.rerun() 
            else:
                st.error("🚨 로그인 실패: 아이디 또는 비밀번호를 확인해주세요.")

# 퀴즈
else:
    if not st.session_state['quiz_finished']:
        idx = st.session_state['current_idx']
        row = quiz_df.iloc[idx]
        
        st.write(f"### {idx + 1}번째 타격 (문제 {idx + 1} / {len(quiz_df)})")
        st.progress((idx + 1) / len(quiz_df))
        
        st.write(f"#### {row['question']}")
        
        user_choice = None
        if row['type'] == 'mcq' or row['type'] == 'ox':
            options = row['options'].split('|')
            default_idx = 0
            if idx in st.session_state['user_answers']:
                default_idx = options.index(st.session_state['user_answers'][idx])
            user_choice = st.radio("정답을 선택하세요:", options, index=default_idx, key=f"q_{idx}")
            
        elif row['type'] == 'short':
            default_val = st.session_state['user_answers'].get(idx, "")
            user_choice = st.text_input("정답을 입력하세요 (띄어쓰기 주의):", value=default_val, key=f"q_{idx}")

        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if idx > 0:
                if st.button("🔙 이전 타석"):
                    st.session_state['user_answers'][idx] = user_choice
                    st.session_state['current_idx'] -= 1
                    st.rerun()
        
        with col3:
            button_label = "타격 종료(결과보기)" if idx == len(quiz_df) - 1 else "다음 타석 🔜"
            if st.button(button_label):
                st.session_state['user_answers'][idx] = user_choice
                if idx < len(quiz_df) - 1:
                    st.session_state['current_idx'] += 1
                else:
                    st.session_state['quiz_finished'] = True
                st.rerun()

    # 퀴즈 결과 및 해설
    else:
        st.write("### 최종 스코어 보드")
        score = 0
        
        for i, row in quiz_df.iterrows():
            user_ans = st.session_state['user_answers'].get(i, "").strip()
            correct_answers = [a.strip() for a in str(row['answer']).split('|')]
            if user_ans in correct_answers:
                score += 1
                
        st.success(f"당신의 최종 타율: {score / len(quiz_df):.3f} (점수: {score} / {len(quiz_df)})")
        if score == len(quiz_df): st.balloons()
        
        st.markdown("---")
        st.write("#### 타석별 리뷰 (정답 및 해설)")
        
        for i, row in quiz_df.iterrows():
            user_ans = st.session_state['user_answers'].get(i, "").strip()
            correct_answers = [a.strip() for a in str(row['answer']).split('|')]
            is_correct = user_ans in correct_answers
            
            if is_correct:
                st.write(f"**{i+1}번째 타격. {row['question']}** [✅ 정답]")
            else:
                st.write(f"**{i+1}번째 타격. {row['question']}** [❌ 오답]")
            
            st.write(f"- **제출한 답:** {user_ans if user_ans else '미입력'}")
            
            ans_display = " 또는 ".join(correct_answers) if len(correct_answers) > 1 else correct_answers[0]
            st.write(f"- **정답:** {ans_display}")
            st.write(f"- **해설:** {row['explanation']}")
            st.write("") 
            
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("다시 도전하기"):
                st.session_state['current_idx'] = 0
                st.session_state['quiz_finished'] = False
                st.session_state['user_answers'] = {}
                st.rerun()
        with col2:
            if st.button("타격장 나가기 (로그아웃)"):
                st.session_state['logged_in'] = False
                st.session_state['current_idx'] = 0
                st.session_state['quiz_finished'] = False
                st.session_state['user_answers'] = {}
                st.rerun()
        print("=== 앱 조작 감지됨 ===")
