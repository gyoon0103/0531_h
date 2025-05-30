import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="Gemini 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 스타일 설정
st.markdown("""
<style>
    .stChat {
        min-height: 400px;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# API 키 검증 및 모델 초기화
try:
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("🚨 .streamlit/secrets.toml 파일에 GOOGLE_API_KEY가 설정되지 않았습니다.")
        st.stop()
    
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-api-key-here":
        st.error("🚨 유효한 Google API 키를 설정해주세요.")
        st.stop()

    # Gemini API 설정
    genai.configure(api_key=GOOGLE_API_KEY)
    
    try:
        # 모델 초기화
        model = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        st.error(f"🚨 Gemini 모델 초기화 중 오류가 발생했습니다: {str(e)}")
        st.stop()

except Exception as e:
    st.error(f"🚨 설정 중 오류가 발생했습니다: {str(e)}")
    st.stop()

# 세션 상태 초기화
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_gemini_response(question):
    """Gemini API를 사용하여 응답을 생성하는 함수"""
    try:
        response = st.session_state.chat.send_message(question)
        if not response.text:
            return "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
        return response.text
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

def format_chat_history():
    """채팅 기록을 포맷팅하는 함수"""
    if not st.session_state.chat_history:
        return "아직 대화 내역이 없습니다."
    
    formatted_history = []
    for idx, message in enumerate(st.session_state.chat_history, 1):
        role = "사용자" if message["role"] == "user" else "Gemini"
        formatted_history.append(f"{idx}. {role}:\n{message['content']}\n")
    
    return "\n".join(formatted_history)

def reset_chat():
    """채팅을 초기화하는 함수"""
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.chat_history = []
    st.session_state.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Streamlit UI
st.title("🤖 Gemini 챗봇")
st.markdown("### Gemini API를 활용한 기본 챗봇 프레임워크입니다.")

# 사이드바 구성
with st.sidebar:
    st.subheader("🛠 채팅 설정")
    if st.button("💫 대화 기록 초기화"):
        reset_chat()
        st.rerun()
    
    # 이전 대화 보기 expander
    with st.expander("📜 이전 대화 보기", expanded=False):
        st.caption(f"대화 시작 시간: {st.session_state.start_time}")
        st.divider()
        st.markdown(format_chat_history())
    
    # 도움말
    with st.expander("❓ 도움말", expanded=False):
        st.markdown("""
        ### 사용 방법
        1. 메시지 입력창에 질문을 입력하세요.
        2. Enter 키를 누르거나 전송 버튼을 클릭하세요.
        3. Gemini AI가 응답을 생성할 때까지 기다려주세요.
        
        ### 기능
        - 💫 대화 기록 초기화: 현재까지의 대화를 모두 지웁니다.
        - 📜 이전 대화 보기: 지금까지의 대화 내용을 확인할 수 있습니다.
        """)

# 구분선 추가
st.divider()

# 메인 채팅 인터페이스
chat_container = st.container()

# 채팅 기록 표시
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 표시
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # AI 응답 생성 및 표시
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("응답을 생성하고 있습니다..."):
                response = get_gemini_response(prompt)
                st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # 스크롤을 최신 메시지로 이동
        st.rerun() 