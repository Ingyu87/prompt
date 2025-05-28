import streamlit as st
import streamlit.components.v1 as components
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
    .copy-tip {
        background-color: #e8f4fd;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-size: 14px;
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
    
    ⚠️ 오직 이런 내용만 부적절함으로 판단하세요:
    - 실제 정치인, 정당 언급
    - 심각한 폭력, 살인, 고문
    - 성적, 음란한 내용
    - 욕설, 혐오 표현

    ✅ 이런 내용은 모두 적절함으로 판단하세요:
    - 만화/애니메이션 캐릭터들의 다툼, 경쟁
    - 전래동화, 설화 캐릭터
    - 친구들끼리 싸움, 갈등
    - 스포츠 경기, 게임 대결
    - 모험, 탐험 이야기
    
    답변: 적절함 또는 부적절함만 답하세요."""
    
    try:
        response = model.generate_content(validation_prompt)
        result = response.text.strip()
        if "적절함" in result:
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
    
    다음 4개 플랫폼에 맞는 프롬프트를 각각 만들어주세요:
    
    1. 투닝매직용: 한국어 단어를 쉼표로 나열, 간단명료하게 (예: 아이들, 우주복, 별들, 밝은 색감, 귀여운 스타일)
    2. 캔바 AI용: 영어 프롬프트, 상세하고 구체적인 설명
    3. 아트봅봅 스쿨용: 초등학생 교육용에 최적화
    4. ChatGPT DALL-E용: 영어 프롬프트, 창의적이고 상세한 묘사
    
    답변 형식:
    **투닝매직**: [프롬프트]
    **캔바 AI**: [프롬프트]  
    **아트봅봅 스쿨**: [프롬프트]
    **ChatGPT**: [프롬프트]"""
    
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
    
    # 경고문구 추가
    st.warning("""
    ⚠️ **작성 시 주의사항**
    - 교육적이고 건전한 내용만 작성해주세요
    - 정치, 혐오, 폭력, 선정적 내용은 금지됩니다
    - 친구들의 갈등, 경쟁, 모험 등은 괜찮습니다
    - 초등학생이 보기에 적절한 내용인지 확인해주세요
    """)
    
    topic = st.text_area("주제 입력", placeholder="예: 우주를 탐험하는 친구들, 숲속의 동물 친구들...", height=100)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🎨 프롬프트 생성하기", use_container_width=True, type="primary", 
                                disabled=not (topic and st.session_state.selected_style and model))
    
    # 다시 만들기 버튼 (프롬프트가 이미 생성된 경우에만 표시)
    if st.session_state.generated_prompts:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 다시 만들기", use_container_width=True, type="secondary"):
                if topic and st.session_state.selected_style and model:
                    with st.spinner("새로운 프롬프트를 생성하는 중..."):
                        is_valid, validation_message = validate_content(model, topic)
                        if not is_valid:
                            st.error(f"🚫 {validation_message}")
                        else:
                            st.session_state.generated_prompts = generate_prompts(model, topic, st.session_state.selected_style)
                            st.success("✨ 새로운 프롬프트가 생성되었습니다!")
                            st.rerun()
    
    if generate_btn and topic and st.session_state.selected_style:
        with st.spinner("내용을 검증하고 프롬프트를 생성하는 중..."):
            is_valid, validation_message = validate_content(model, topic)
            if not is_valid:
                st.error(f"🚫 {validation_message}")
                st.markdown('<div class="warning-box">💡 교육적이고 건전한 주제로 다시 작성해주세요.<br>예시: 과학 탐험, 역사 여행, 자연 관찰, 우정 이야기 등</div>', unsafe_allow_html=True)
            else:
                st.session_state.generated_prompts = generate_prompts(model, topic, st.session_state.selected_style)
    
    if st.session_state.generated_prompts:
        st.markdown("---")
        st.markdown("### 🎯 생성된 프롬프트")
        
        # 복사 안내
        st.markdown('<div class="copy-tip">💡 <strong>복사 방법</strong>: 📋 복사 버튼을 클릭하면 자동으로 복사됩니다!</div>', unsafe_allow_html=True)
        
        # 새로고침 안내
        st.info("💡 같은 주제로 다른 버전의 프롬프트가 필요하면 '🔄 다시 만들기' 버튼을 사용하세요!")
        
        # 각 플랫폼별 프롬프트 표시
        platform_info = {
            "투닝매직": {"url": "https://tooning.io/", "desc": "간단한 한국어 프롬프트", "icon": "🎭"},
            "캔바 AI": {"url": "https://www.canva.com/", "desc": "상세한 영어 프롬프트", "icon": "🎨"}, 
            "아트봅봅 스쿨": {"url": "https://school-teacher.art-bonbon.com/", "desc": "교육용 최적화 프롬프트", "icon": "🎪"},
            "ChatGPT": {"url": "https://chat.openai.com/", "desc": "ChatGPT DALL-E용 창의적 프롬프트", "icon": "🤖"}
        }
        
        for platform, prompt_text in st.session_state.generated_prompts.items():
            if platform in platform_info:
                info = platform_info[platform]
                
                st.markdown(f"#### {info['icon']} [{platform}]({info['url']})")
                st.markdown(f"*{info['desc']}*")
                
                # 자동 복사 가능한 텍스트 영역과 복사 버튼
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text_area(
                        "",
                        value=prompt_text,
                        height=120,
                        key=f"prompt_{platform}_{hash(prompt_text) % 1000}",
                        label_visibility="collapsed"
                    )
                with col2:
                    copy_button_key = f"btn_{platform}_{hash(prompt_text) % 1000}"
                    if st.button("📋 복사", key=copy_button_key):
                        # JavaScript로 클립보드 복사
                        escaped_text = prompt_text.replace('`', '\\`').replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
                        components.html(f"""
                        <script>
                        navigator.clipboard.writeText(`{escaped_text}`).then(function() {{
                            alert('✅ 프롬프트가 복사되었습니다!');
                        }}).catch(function(err) {{
                            console.error('복사 실패: ', err);
                            alert('❌ 복사에 실패했습니다. 수동으로 복사해주세요.');
                        }});
                        </script>
                        """, height=0)
                
                st.markdown("---")
        
        # 사용 안내
        st.markdown("### 📋 사용 방법")
        st.markdown("""
        1. **투닝매직**: 한국어 프롬프트를 복사하여 투닝매직 사이트에 붙여넣기
        2. **캔바 AI**: 영어 프롬프트를 캔바의 AI 이미지 생성기에 입력
        3. **아트봅봅 스쿨**: 교육용 프롬프트를 아트봡봉 스쿨에서 활용
        4. **ChatGPT**: ChatGPT에 접속하여 DALL-E 이미지 생성에 활용
        
        각 사이트의 특성에 맞게 최적화된 프롬프트를 제공합니다! 🎨
        """)

if __name__ == "__main__":
    main()
