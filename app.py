import streamlit as st
from crewai import Crew
from agents import content_researcher, content_writer
from tasks import research_task, writing_task
from tools import create_pdf, create_docx

# ─────────────────────────────────────────────
# 🎨 PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Content Generator Pro",
    page_icon="🤖",
    layout="centered"
)

# ─────────────────────────────────────────────
# 💅 CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        border: 1px solid #313244;
    }
    .metric-label { font-size: 12px; color: #a6adc8; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 700; color: #cdd6f4; }

    .history-card {
        background: #1e1e2e;
        border-left: 3px solid #89b4fa;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        cursor: pointer;
    }
    .history-title { font-weight: 600; color: #cdd6f4; font-size: 14px; }
    .history-meta  { font-size: 11px; color: #6c7086; margin-top: 2px; }

    .tag {
        display: inline-block;
        background: #313244;
        color: #cba6f7;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        margin-right: 4px;
    }
    .content-box {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 20px;
        white-space: pre-wrap;
        font-family: 'Georgia', serif;
        font-size: 15px;
        line-height: 1.75;
        color: #cdd6f4;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 🗂️ SESSION STATE INIT
# ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []          # list of dicts

if "current_content" not in st.session_state:
    st.session_state.current_content = None

if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = {}


# ─────────────────────────────────────────────
# 🎯 HEADER
# ─────────────────────────────────────────────
st.title("🤖 AI Content Generator Pro")
st.caption("CrewAI · Ollama · qwen2.5:1.5b")

# ─────────────────────────────────────────────
# ⚙️ SIDEBAR — Settings + History
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Content Settings")

    content_type = st.selectbox(
        "Content Type",
        ["Blog Post", "LinkedIn Post", "YouTube Script", "Instagram Caption", "Email"]
    )

    tone = st.selectbox(
        "Tone",
        ["Professional", "Casual", "Funny", "Formal", "Motivational"]
    )

    word_count = st.slider("Word Count", 100, 500, 200, step=50)

    st.divider()

    # ── HISTORY PANEL ──────────────────────────
    st.subheader("🕓 History")

    if not st.session_state.history:
        st.caption("No generations yet.")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - 1 - i
            with st.container():
                st.markdown(
                    f"""
                    <div class="history-card">
                        <div class="history-title">📌 {item['topic'][:30]}{'...' if len(item['topic'])>30 else ''}</div>
                        <div class="history-meta">
                            <span class="tag">{item['content_type']}</span>
                            <span class="tag">{item['tone']}</span>
                            {item['words']}w
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Load", key=f"load_{idx}"):
                    st.session_state.current_content = item["content"]
                    st.session_state.last_inputs = {
                        "topic": item["topic"],
                        "content_type": item["content_type"],
                        "tone": item["tone"],
                        "word_count": item["words"],
                    }

    if st.session_state.history:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()


# ─────────────────────────────────────────────
# 💡 MAIN INPUT
# ─────────────────────────────────────────────
topic = st.text_input(
    "💡 Enter Topic",
    placeholder="Example: AI in Gaming",
    value=st.session_state.last_inputs.get("topic", "")
)

col1, col2, col3 = st.columns([2, 2, 1])
generate    = col1.button("🚀 Generate",   use_container_width=True)
regenerate  = col2.button("🔄 Regenerate", use_container_width=True,
                           disabled=st.session_state.current_content is None)
clear       = col3.button("🧹 Clear",      use_container_width=True)


# ─────────────────────────────────────────────
# 🔧 HELPER — Run Crew
# ─────────────────────────────────────────────
def run_crew(topic, content_type, tone, word_count):
    researcher = content_researcher()
    writer     = content_writer()
    research   = research_task(researcher, topic)
    writing    = writing_task(writer, topic, content_type, tone, word_count, research)
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research, writing],
        verbose=False
    )
    return str(crew.kickoff())


def reading_time(text):
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"


def save_to_history(topic, content_type, tone, content):
    st.session_state.history.append({
        "topic": topic,
        "content_type": content_type,
        "tone": tone,
        "content": content,
        "words": len(content.split()),
    })


# ─────────────────────────────────────────────
# 🚀 GENERATE / REGENERATE
# ─────────────────────────────────────────────
should_run = (generate or regenerate) and topic

if should_run:
    with st.spinner("🧠 AI Agents are researching and writing..."):
        try:
            content = run_crew(topic, content_type, tone, word_count)
            st.session_state.current_content = content
            st.session_state.last_inputs = {
                "topic": topic,
                "content_type": content_type,
                "tone": tone,
                "word_count": word_count,
            }
            save_to_history(topic, content_type, tone, content)
            st.success("✅ Content generated successfully!")
        except Exception as e:
            err = str(e)
            if "connection" in err.lower() or "ollama" in err.lower():
                st.error("❌ Cannot reach Ollama. Make sure it's running: `ollama serve`")
            elif "model" in err.lower():
                st.error("❌ Model not found. Run: `ollama pull qwen2.5:1.5b`")
            else:
                st.error(f"❌ Unexpected error: {err}")
            st.stop()


# ─────────────────────────────────────────────
# 📊 OUTPUT DISPLAY
# ─────────────────────────────────────────────
if st.session_state.current_content:
    content = st.session_state.current_content
    words      = len(content.split())
    characters = len(content)
    sentences  = content.count(".") + content.count("!") + content.count("?")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📝 Words",      words)
    m2.metric("🔤 Characters", characters)
    m3.metric("📖 Read Time",  reading_time(content))
    m4.metric("💬 Sentences",  sentences)

    st.divider()

    # Content display
    st.subheader("✨ Generated Content")
    st.markdown(
        f'<div class="content-box">{content}</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # Action buttons
    a1, a2, a3 = st.columns(3)

    with a1:
        pdf_data = create_pdf(content)
        st.download_button(
            "📄 Download PDF",
            data=pdf_data,
            file_name=f"content_{content_type.lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with a2:
        docx_data = create_docx(content)
        st.download_button(
            "📝 Download DOCX",
            data=docx_data,
            file_name=f"content_{content_type.lower().replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    with a3:
        st.download_button(
            "📋 Download TXT",
            data=content.encode("utf-8"),
            file_name=f"content_{content_type.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ─────────────────────────────────────────────
# 🧹 CLEAR
# ─────────────────────────────────────────────
if clear:
    st.session_state.current_content = None
    st.session_state.last_inputs = {}
    st.rerun()