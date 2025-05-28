import streamlit as st
import google.generativeai as genai
import os

# 페이지 설정
st.set_page_config(
    page_title="🎨 교육용 이미지 프롬프트 생성기",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .watermark {
        position: fixed;
        bottom: 20px;
        left: 20px;
        background-color: rgba(74, 144, 226, 0.8);
        color: white;
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 스타일 옵션 정의
STYLE_OPTIONS = {
    "🎭 캐릭터 애니메이션": {"icon": "🎭", "name": "캐릭터 애니메이션", "description": "귀여운 캐릭터와 애니메이션 스타일"},
    "📚 한국 웹툰": {"icon": "📚", "name": "한국 웹툰", "description": "한국적인 웹툰 스타일"},
    "🎪 3D 캐릭터": {"icon": "🎪", "name": "3D 캐릭터", "description": "입체적인 3D 캐릭터 스타일"},
    "👑 파워풀 캐릭터": {"icon": "👑", "name": "파워풀 캐릭터", "description": "강인하고 멋진 캐릭터"},
    "✏️ 낙서 캐릭터": {"icon": "✏️", "name": "낙서 캐릭터", "description": "자유로운 낙서 스타일"},
    "📷 수채화": {"icon": "📷", "name": "수채화", "description": "부드러운 수채화 느낌"},
    "🍄 동화적": {"icon": "🍄", "name": "동화적", "description": "동화책 같은 따뜻한 느낌"},
    "📸 실제 사진": {"icon": "📸", "name": "실제 사진", "description": "사실적인 사진 스타일"},
    "🏠 인물극": {"icon": "🏠", "name": "인물극", "description": "드라마틱한 인물 중심"},
    "🔮 클레이 모델": {"icon": "🔮", "name": "클레이 모델", "description": "점토로 만든 듯한 질감"}
}

def setup_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🚨 GEMINI_API_KEY가 설정되지 않았습니다.")
        st.info("Streamlit Secrets 또는 환경변수에서 GEMINI_API_KEY를 설정해주세요.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def validate_content(model, topic):
    if not model:
        return False, "API 설정이 필요합니다."
    
    validation_prompt = f"""다음 주제가 초등학생용 교육 콘텐츠로 적절한지 판단해주세요:
    주제: "{topic}"
    
    판단 기준:
    - 교육적 가치가 있는가?
    - 초등학생에게 적절한 내용인가?
    - 비속어, 폭력적 내용, 성적 내용이 없는가?
    
    답변 형식: 판단결과: [적절함/부적절함], 이유: [설명]"""
    
    try:
        response = model.generate_content(validation_prompt)
        result = response.text.strip()
        if "적절함" in result and "부적절함" not in result:
            return True, "교육적으로 적절한 주제입니다."
        else:
            return False, "교육적으로 부적절한 내용이 포함되어 있습니다."
    except Exception as e:
        return False, f"내용 검증 중 오류: {str(e)}"

def generate_prompts(model, topic, style):
    if not model:
        return {}
    
    style_info = STYLE_OPTIONS.get(style, {"name": style, "description": ""})
    prompt = f"""교육용 이미지 생성 프롬프트를 만들어주세요.
    
    주제: {topic}
    스타일: {style_info['name']} - {style_info['description']}
    
    다음 3개 플랫폼에 맞는 프롬프트를 각각 만들어주세요:
    
    1. 투닝매직용: 한국어 가능, 간단하고 직관적인 표현
    2. 캔바 AI용: 영어 프롬프트, 상세하고 구체적인 설명
    3. 아트봅봅 스쿨용: 초등학생 교육용에 최적화
    
    답변 형식:
    **투닝매직**: [프롬프트]
    **캔바 AI**: [프롬프트]  
    **아트봉봉 스쿨**: [프롬프트]"""
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        prompts = {}
        sections = result.split("**")
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                platform = sections[i].strip().rstrip(":")
                content = sections[i + 1].strip()
                prompts[platform] = content
        return prompts
    except Exception as e:
        st.error(f"프롬프트 생성 오류: {str(e)}")
        return {}

def main():
    st.markdown('<h1 class="main-header">🎨 교육용 이미지 프롬프트 생성기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">원하는 스타일을 클릭해보세요. 각자 다른 느낌의 만화가 만들어져요.</p>', unsafe_allow_html=True)
    st.markdown('<div class="watermark">서울가동초 백인규</div>', unsafe_allow_html=True)
    
    model = setup_gemini()
    
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = None
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = {}
    
    st.markdown("### 만화/사진 스타일을 선택하세요")
    cols = st.columns(3)
    style_keys = list(STYLE_OPTIONS.keys())
    
    for i, style_key in enumerate(style_keys):
        col_idx = i % 3
        style_info = STYLE_OPTIONS[style_key]
        with cols[col_idx]:
            if st.button(f"{style_info['icon']} {style_info['name']}", key=f"style_btn_{i}", use_container_width=True):
                st.session_state.selected_style = style_key
                st.rerun()
    
    if st.session_state.selected_style:
        selected_info = STYLE_OPTIONS[st.session_state.selected_style]
        st.success(f"✅ 선택된 스타일: {selected_info['icon']} {selected_info['name']}")
    
    st.markdown("---")
    st.markdown("### 생성하고 싶은 주제를 작성해주세요")
    
    topic = st.text_area("주제 입력", placeholder="예: 우주를 탐험하는 친구들, 숲속의 동물 친구들...", height=100)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🎨 프롬프트 생성하기", use_container_width=True, type="primary", 
                                disabled=not (topic and st.session_state.selected_style and model))
    
    if generate_btn and topic and st.session_state.selected_style:
        with st.spinner("내용을 검증하고 프롬프트를 생성하는 중..."):
            is_valid, validation_message = validate_content(model, topic)
            if not is_valid:
                st.error(f"🚫 {validation_message}")
                st.markdown('<div class="warning-box">💡 교육적이고 건전한 주제로 다시 작성해주세요.</div>', unsafe_allow_html=True)
            else:
                st.session_state.generated_prompts = generate_prompts(model, topic, st.session_state.selected_style)
    
    if st.session_state.generated_prompts:
        st.markdown("---")
        st.markdown("### 🎯 생성된 프롬프트")
        for platform, prompt_text in st.session_state.generated_prompts.items():
            st.markdown(f"#### {platform}")
            st.code(prompt_text, language="text")
            st.info("💡 위 텍스트를 복사하여 해당 사이트에서 사용하세요!")
            st.markdown("---")

if __name__ == "__main__":
    main()
