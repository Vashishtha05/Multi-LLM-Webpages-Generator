import os
import time
import base64

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LLM Benchmark Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* Global */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #667eea 100%);
        background-size: 400% 400%;
        animation: gradientShift 8s ease infinite;
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.97);
        backdrop-filter: blur(12px);
    }

    /* Cards */
    .glass-card {
        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(10px);
        border-radius: 1.25rem;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom: 1.5rem;
    }

    /* Metric badges */
    .metric-row {
        display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem;
    }
    .metric-badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; font-weight: 600; border-radius: 999px; font-size: 0.85rem;
    }
    .metric-badge.green {
        background: linear-gradient(135deg, #10b981, #059669);
    }
    .metric-badge.amber {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    /* Preview frame */
    .preview-container {
        border: 1px solid #e5e7eb;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        background: #fff;
    }
    .preview-container iframe {
        width: 100%;
        height: 620px;
        border: none;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.75rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.7);
        border-radius: 0.75rem 0.75rem 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: white;
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }
    .app-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .app-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Models Configuration ───────────────────────────────────────────────────────
MODEL_CATALOG = {
    "openai": {
        "label": "OpenAI GPT-4o-mini",
        "model_id": "gpt-4o-mini",
        "icon": "🟢",
        "client_key": "openai",
    },
    "claude": {
        "label": "Claude 3.5 Sonnet",
        "model_id": "anthropic/claude-3.5-sonnet",
        "icon": "🟠",
        "client_key": "openrouter",
    },
    "gemini": {
        "label": "Google Gemini 2.0 Flash",
        "model_id": "google/gemini-2.0-flash-001",
        "icon": "🔵",
        "client_key": "openrouter",
    },
}

SYSTEM_PROMPT = """You are a professional landing page HTML generator.
Create a complete, beautiful, single-file HTML landing page for the given product or service.
Include:
- A compelling hero section with CTA
- Features section with icons (use unicode emoji for icons)
- Pricing or benefits section
- Testimonials (create realistic ones)
- Footer with contact info
- Modern CSS with gradients, shadows and smooth transitions
- Fully responsive design
- NO external dependencies - all CSS must be in inline <style> tags
- NO external images - use CSS gradients / emoji / unicode for visuals
Return ONLY the complete HTML code, no markdown fences, no explanation."""


# ─── Client helpers ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_clients():
    clients = {}
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openai_key:
        clients["openai"] = OpenAI(api_key=openai_key)
    if openrouter_key:
        clients["openrouter"] = OpenAI(
            api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"
        )
    return clients


def generate_page(client: OpenAI, model_id: str, description: str, max_tokens: int):
    """Call the LLM and return (html_string, elapsed_seconds)."""
    start = time.time()
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": description},
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    elapsed = time.time() - start
    content = response.choices[0].message.content or ""
    # Strip markdown fences if the model wraps them
    content = content.strip()
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:])
    if content.endswith("```"):
        content = "\n".join(content.split("\n")[:-1])
    return content.strip(), round(elapsed, 2)


def render_html_preview(html_content: str, key: str):
    """Render an HTML string inside an iframe using base64 data URI."""
    encoded = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    iframe_html = f"""
    <div class="preview-container">
        <iframe src="data:text/html;base64,{encoded}"></iframe>
    </div>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="app-header">
    <h1>⚡ LLM Benchmark Studio</h1>
    <p>Generate &amp; compare landing pages from multiple LLMs side-by-side</p>
</div>
""",
    unsafe_allow_html=True,
)

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Configuration")

    clients = get_clients()
    available = {
        k: v for k, v in MODEL_CATALOG.items() if v["client_key"] in clients
    }

    if not available:
        st.error("No API keys found. Add keys to your `.env` file.")
        st.stop()

    description = st.text_area(
        "Product / Service Description",
        height=180,
        placeholder="A SaaS project management tool for remote teams with real-time collaboration, Gantt charts, and AI-powered task prioritisation...",
    )

    st.markdown("---")

    selected_models = st.multiselect(
        "Select Models to Benchmark",
        options=list(available.keys()),
        default=list(available.keys())[:2],
        format_func=lambda k: f"{MODEL_CATALOG[k]['icon']}  {MODEL_CATALOG[k]['label']}",
    )

    st.markdown("---")

    max_tokens = st.slider(
        "⚡ Max Tokens",
        min_value=500,
        max_value=4000,
        value=2000,
        step=100,
        help="Higher = more detailed pages, but slower generation.",
    )

    st.markdown("---")

    generate_btn = st.button(
        "✨  Generate Pages",
        use_container_width=True,
        type="primary",
        disabled=not description or not selected_models,
    )

# ─── Main Area ───────────────────────────────────────────────────────────────────
if generate_btn and description and selected_models:
    results = {}

    progress_bar = st.progress(0, text="Starting generation...")
    total = len(selected_models)

    for idx, model_key in enumerate(selected_models):
        info = MODEL_CATALOG[model_key]
        client = clients[info["client_key"]]

        progress_bar.progress(
            (idx) / total,
            text=f"{info['icon']}  Generating with **{info['label']}**...",
        )

        try:
            html_content, elapsed = generate_page(
                client, info["model_id"], description, max_tokens
            )
            results[model_key] = {
                "html": html_content,
                "time": elapsed,
                "error": None,
            }
        except Exception as exc:
            results[model_key] = {
                "html": "",
                "time": 0,
                "error": str(exc),
            }

    progress_bar.progress(1.0, text="✅  All models finished!")
    time.sleep(0.5)
    progress_bar.empty()

    # Store in session for persistence
    st.session_state["results"] = results
    st.session_state["selected_models"] = selected_models

# ─── Display Results ─────────────────────────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    selected_models = st.session_state["selected_models"]

    # Stats row
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    cols = st.columns(len(selected_models))
    for col, model_key in zip(cols, selected_models):
        info = MODEL_CATALOG[model_key]
        r = results[model_key]
        with col:
            if r["error"]:
                st.metric(
                    label=f"{info['icon']} {info['label']}",
                    value="Error",
                    delta=r["error"],
                    delta_color="inverse",
                )
            else:
                st.metric(
                    label=f"{info['icon']} {info['label']}",
                    value=f"{r['time']}s",
                    delta=f"{len(r['html']):,} chars",
                )
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabbed previews
    tabs = st.tabs(
        [
            f"{MODEL_CATALOG[k]['icon']}  {MODEL_CATALOG[k]['label']}"
            for k in selected_models
        ]
    )

    for tab, model_key in zip(tabs, selected_models):
        info = MODEL_CATALOG[model_key]
        r = results[model_key]

        with tab:
            if r["error"]:
                st.error(f"Generation failed: {r['error']}")
            else:
                view_col, code_col = st.columns([3, 1])

                with view_col:
                    st.markdown(
                        f"**Preview** — _{info['label']}_ ({r['time']}s)",
                    )
                    render_html_preview(r["html"], key=model_key)

                with code_col:
                    st.markdown("**Actions**")
                    st.download_button(
                        "⬇️  Download HTML",
                        data=r["html"],
                        file_name=f"{model_key}_landing_page.html",
                        mime="text/html",
                        use_container_width=True,
                    )
                    with st.expander("📄 View Source"):
                        st.code(r["html"], language="html", line_numbers=True)

else:
    st.markdown(
        """
    <div class="glass-card" style="text-align:center; padding: 4rem 2rem;">
        <h2 style="color:#6b7280;">👈  Fill the sidebar &amp; click Generate</h2>
        <p style="color:#9ca3af;">Select your models, describe your product, and compare LLM outputs side-by-side.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
