import re

import streamlit as st
import google.generativeai as genai

_CSS = """
<style>
/* ── Google color palette ──────────────────────────────────────── */
/* Blue   #4285F4  |  Red    #EA4335                               */
/* Yellow #FBBC05  |  Green  #34A853                               */
/* Surface #F8F9FA |  Text   #202124  |  Secondary text #5F6368   */
/* Border  #DADCE0                                                 */

/* ── Page background ───────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: #F8F9FA;
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
    margin-bottom: 0.3rem;
    /* Spell out each letter in Google brand colours */
    background: linear-gradient(
        90deg,
        #4285F4  0%  16%,   /* G – blue   */
        #EA4335 16%  33%,   /* o – red    */
        #FBBC05 33%  50%,   /* o – yellow */
        #4285F4 50%  58%,   /* g – blue   */
        #34A853 58%  75%,   /* l – green  */
        #EA4335 75% 100%    /* e – red    */
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: #5F6368;
    font-size: 1.05rem;
    margin-top: 0;
}

/* ── Response card ─────────────────────────────────────────────── */
.response-card {
    background: #FFFFFF;
    border: 1px solid #DADCE0;
    border-left: 4px solid #4285F4;
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    color: #202124;
    font-size: 1rem;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    margin-top: 1rem;
    box-shadow: 0 1px 3px rgba(60,64,67,0.12);
}
.response-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4285F4;
    margin-bottom: 0.4rem;
}

/* ── Error card ────────────────────────────────────────────────── */
.error-card {
    background: #FFF3F2;
    border: 1px solid #F5C6C2;
    border-left: 4px solid #EA4335;
    border-radius: 8px;
    padding: 1.2rem 1.6rem;
    color: #C5221F;
    font-size: 0.97rem;
    margin-top: 1rem;
}

/* ── Buttons ───────────────────────────────────────────────────── */
[data-testid="stButton"] button {
    background: #4285F4 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.45rem 1.2rem !important;
    font-weight: 600 !important;
    transition: box-shadow 0.2s, background 0.2s !important;
    box-shadow: 0 1px 2px rgba(60,64,67,0.30) !important;
}
[data-testid="stButton"] button:hover {
    background: #1a73e8 !important;
    box-shadow: 0 2px 6px rgba(60,64,67,0.35) !important;
}

/* ── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #DADCE0;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #202124 !important; }
[data-testid="stSidebar"] h2 {
    color: #4285F4 !important;
    font-size: 1.1rem;
}

/* ── External link buttons ─────────────────────────────────────── */
.ext-btn {
    display: inline-block;
    width: 100%;
    text-align: center;
    padding: 0.45rem 0;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.9rem;
    text-decoration: none !important;
    margin-bottom: 0.5rem;
    transition: box-shadow 0.2s;
    box-shadow: 0 1px 2px rgba(60,64,67,0.25);
}
.ext-btn:hover { box-shadow: 0 2px 6px rgba(60,64,67,0.35); }
.btn-github {
    background: #202124;
    color: #fff !important;
}
.btn-sponsor {
    background: #EA4335;
    color: #fff !important;
}

/* ── Warning/info text ─────────────────────────────────────────── */
[data-testid="stAlert"] p { color: #202124 !important; }
[data-testid="stSpinner"] p { color: #4285F4 !important; }
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
        page_icon=":robot_face:",
        layout="centered",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Hero header ────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero">
            <h1>Google AI Studio</h1>
            <p>Chat with the latest Gemini models using your own API key.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")

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
               View on GitHub
            </a>
            <a class="ext-btn btn-sponsor"
               href="https://github.com/sponsors/gituserc1140"
               target="_blank" rel="noopener noreferrer">
               Sponsor on GitHub
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

    if st.button("Generate", disabled=not prompt.strip()):
        genai.configure(api_key=api_key)
        with st.spinner("Generating response…"):
            try:
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(prompt.strip())
                st.markdown('<div class="response-label">Response</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="response-card">{response.text}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                err_str = str(exc)
                # Parse retry delay from the error message if present
                retry_match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", err_str)
                retry_seconds = int(retry_match.group(1)) if retry_match else None

                if "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str:
                    quota_msg = (
                        "API quota exceeded for this key. "
                        "You have hit the free-tier rate limit for the Gemini API."
                    )
                    if retry_seconds is not None:
                        unit = "second" if retry_seconds == 1 else "seconds"
                        quota_msg += f" Please wait {retry_seconds} {unit} before trying again."
                    quota_msg += (
                        " To avoid this, use a paid API key or enable billing at "
                        "https://aistudio.google.com/apikey."
                    )
                    st.markdown(
                        f'<div class="error-card">{quota_msg}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="error-card">Error: {exc}</div>',
                        unsafe_allow_html=True,
                    )


if __name__ == "__main__":
    main()