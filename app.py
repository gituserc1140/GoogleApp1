import streamlit as st
import google.generativeai as genai

_CSS = """
<style>
/* ── Page background ───────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Hero banner ───────────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #34d399, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p {
    color: #cbd5e1;
    font-size: 1.05rem;
    margin-top: 0;
}

/* ── Response card ─────────────────────────────────────────────── */
.response-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(96,165,250,0.35);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    color: #e2e8f0;
    font-size: 1rem;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    margin-top: 1rem;
}
.response-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #60a5fa;
    margin-bottom: 0.4rem;
}

/* ── Error card ────────────────────────────────────────────────── */
.error-card {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.45);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    color: #fca5a5;
    font-size: 0.97rem;
    margin-top: 1rem;
}

/* ── Buttons ───────────────────────────────────────────────────── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #059669, #2563eb) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.2rem !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

/* ── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85);
    border-right: 1px solid rgba(96,165,250,0.2);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h2 {
    color: #60a5fa !important;
    font-size: 1.1rem;
}

/* ── External link buttons ─────────────────────────────────────── */
.ext-btn {
    display: inline-block;
    width: 100%;
    text-align: center;
    padding: 0.45rem 0;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none !important;
    margin-bottom: 0.5rem;
    transition: opacity 0.2s;
}
.ext-btn:hover { opacity: 0.85; }
.btn-github {
    background: #24292e;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.15);
}
.btn-sponsor {
    background: linear-gradient(135deg, #db61a2, #ea4aaa);
    color: #fff !important;
}

/* ── Warning/info text ─────────────────────────────────────────── */
[data-testid="stAlert"] p { color: #ffffff !important; }
[data-testid="stSpinner"] p { color: #60a5fa !important; }
</style>
"""

# Default model list shown before API key is entered
_DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def fetch_models(api_key: str) -> list[str]:
    """Return generate-content-capable Gemini model names for the given key.

    Silently falls back to ``_DEFAULT_MODELS`` if the API call fails for any
    reason (e.g. invalid key, network error, quota exceeded).
    """
    try:
        genai.configure(api_key=api_key)
        models = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
            and m.name.startswith("models/gemini")
        ]
        return sorted(models) if models else _DEFAULT_MODELS
    except Exception:
        return _DEFAULT_MODELS


def main():
    st.set_page_config(
        page_title="Google AI Studio",
        page_icon="🤖",
        layout="centered",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Hero header ────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero">
            <h1>🤖 Google AI Studio</h1>
            <p>Chat with the latest Gemini models using your own API key.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Settings")

        api_key_input = st.text_input(
            "Google AI Studio API Key",
            type="password",
            help="Get your free key at https://aistudio.google.com/apikey",
        )
        stripped_key = api_key_input.strip()

        if stripped_key:
            st.session_state["api_key"] = stripped_key

        api_key = st.session_state.get("api_key", "")

        # Model selector – populated dynamically once a key is available
        if api_key:
            if "available_models" not in st.session_state or st.session_state.get("models_key") != api_key:
                with st.spinner("Loading models…"):
                    st.session_state["available_models"] = fetch_models(api_key)
                    st.session_state["models_key"] = api_key
            model_list = st.session_state["available_models"]
        else:
            model_list = _DEFAULT_MODELS

        selected_model = st.selectbox(
            "Model",
            model_list,
            help="Models are loaded from your API key. Select the one you want to use.",
        )

        st.divider()

        # ── GitHub / Sponsors links ────────────────────────────────
        st.markdown(
            """
            <a class="ext-btn btn-github"
               href="https://github.com/gituserc1140/GoogleApp1"
               target="_blank" rel="noopener noreferrer">
               🐙 View on GitHub
            </a>
            <a class="ext-btn btn-sponsor"
               href="https://github.com/sponsors/gituserc1140"
               target="_blank" rel="noopener noreferrer">
               ❤️ Sponsor on GitHub
            </a>
            """,
            unsafe_allow_html=True,
        )

    # ── Main area ──────────────────────────────────────────────────
    if not api_key:
        st.warning("Enter your Google AI Studio API key in the sidebar to get started.")
        st.stop()

    st.markdown(f"**Model:** `{selected_model}`")

    prompt = st.text_area(
        "Your prompt",
        placeholder="Ask anything…",
        height=140,
    )

    if st.button("✨ Generate", disabled=not prompt.strip()):
        genai.configure(api_key=api_key)
        with st.spinner("Generating response…"):
            try:
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt.strip())
                st.markdown('<div class="response-label">🤖 Response</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="response-card">{response.text}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.markdown(
                    f'<div class="error-card">⚠️ {exc}</div>',
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()