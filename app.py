# app.py — ExoCimarron (Space Apps MVP)

import os, json, requests, joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit.components.v1 import html as html_embed

# =========================
# CONFIG / BRANDING
# =========================
BRAND = "ExoVision"
st.set_page_config(page_title=f"{BRAND} — Space Apps MVP", page_icon="🪐", layout="wide")

# =========================
# ASSETS
# =========================
IMAGES = {
    "exoplanets": "https://media.hswstatic.com/eyJidWNrZXQiOiJjb250ZW50Lmhzd3N0YXRpYy5jb20iLCJrZXkiOiJnaWZcL2V4b3BsYW5ldHMtMS5qcGciLCJlZGl0cyI6eyJyZXNpemUiOnsid2lkdGgiOjgyOH0sInRvRm9ybWF0IjoiYXZpZiJ9fQ==",
    "nasa_logo":  "https://images.seeklogo.com/logo-png/9/1/nasa-logo-png_seeklogo-97034.png",
    "kepler":     "https://images-assets.nasa.gov/image/PIA18904/PIA18904~large.jpg?w=1920&h=1536&fit=clip&crop=faces%2Cfocalpoint",
    "transit":    "https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2003/06/planet_transit/9798645-3-eng-GB/Planet_transit_pillars.jpg",
    "astro_gif":  "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDBnNDF6Zmh3anF3bGRrMjRya2Q3M2hibXZjNGJ3NGtnZWh0YThmMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlO4V8iCRME3i0g/giphy.gif",
    "research":   "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2VyOTJsdGdibTJicGIwdm52YWV3dDJ5dndib20zN3Rxd2JpY2M2cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0GsNMsRwDKKMjiwIe5/giphy.gif",
    "dataset":    "https://github.com/luigicast/images/blob/main/goodImageDataset.png?raw=true",
    "ai_model":   "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDJ5bDU3bmxqYThzOThwa2I3M21rY2lnZDhsNm42b3YxMGdsNzRwMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LR5ZBwZHv02lmpVoEU/giphy.gif",
    "chatbot":    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWE1MzRyM2g3ZG50dnZodzYyNmhhZmt5ZGYwOHJvanlnZmw0dGhxbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S60CrN9iMxFlyp7uM8/giphy.gif",
    "simulator":  "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTZ1MWo4aTQwaDJkbXZnd2JnZjV2ZmtvaW83YmpmMzEyNzNncjJieiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hsubjoiDroLg4AYyUO/giphy.gif",
    "testing":    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjhremVrb3JybnA4eDU0em43eXd5cHc5bHV4OWRqdmFvdHprbXV2eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gw3IWyGkC0rsazTi/giphy.gif",
    "presentation": "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExam83bzgxZTd6aHpuYmQxczloeWdhaHoxbzczOWVyOWI2ZDR0MWEycyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/U3dIoNBOyfTkA/giphy.gif",
    "team":       "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExa24zZW53bGRsNjZobG9pdWlqbXcxbHdubHZqZTkyeWVxMHR5c3BoMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9yssegcqq1WDlPKdP4/giphy.gif",
}

def show_img(src, caption=None):
    try:
        st.image(src, caption=caption, use_container_width=True)
    except Exception:
        st.info("No pude renderizar esta imagen directamente. Ábrela en nueva pestaña:")
        st.link_button("Abrir imagen", src)

# =========================
# GLOBAL THEME (dark elegant)
# =========================
GLOBAL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@400;600;800&display=swap');
:root{ --bg:#070b18; --bg2:#0b1020; --fg:#e6f1ff; --muted:#9bb3c8; }
html,body,[class*="css"]{ font-family:'Inter',system-ui; color:var(--fg); }
h1,h2,h3,h4{ font-family:'Orbitron',sans-serif!important; letter-spacing:.5px; color:#b7e2ff; }

[data-testid="stAppViewContainer"]{
  background:
   radial-gradient(1200px 600px at 20% 0%, rgba(255,255,255,.06), transparent 60%),
   radial-gradient(1000px 600px at 80% 0%, rgba(255,255,255,.03), transparent 60%),
   linear-gradient(180deg, var(--bg2), var(--bg));
}
.block{ background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12);
  border-radius:18px; padding:18px; box-shadow:0 16px 40px rgba(0,0,0,.30); }

/* Plotly dark margin tweaks */
.css-1kyxreq, .plot-container.plotly{ border-radius:14px; overflow:hidden }
</style>
"""
html_embed(GLOBAL_STYLE, height=0)

# =========================
# ROUTES / NAV / STATE
# =========================
ROUTES = {
    "home":    "Home",
    "learn":   "Learn more",
    "predict": "Predict IA",
    "game":    "Play ",
    "chat":    "Chat with ExoCimarron",
    "about":   "About MVP",
}
PAGES = list(ROUTES.values())

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = ROUTES["home"]
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = None
    if "predictor_values" not in st.session_state:
        st.session_state.predictor_values = {}
init_state()

def goto_page(label: str):
    st.session_state.page = label


# --- Sidebar hero: GIF + título centrados ---
st.sidebar.markdown("""
<style>
.sb-hero{
  display:grid; place-items:center; text-align:center;
  margin: 4px 0 14px 0;
}
.sb-hero img{
  width: 200px; height:auto;
  border-radius:16px;
  border:1px solid rgba(255,255,255,.18);
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
}
.sb-hero h1{
  font-family:'Orbitron',sans-serif;
  font-size: 22px; line-height:1.15;
  margin: 10px 0 0 0; letter-spacing:.4px;
  color:#e6f1ff;
}
.sb-hero small{
  color:#9bb3c8; letter-spacing:.2px;
}
</style>

<div class="sb-hero">
  <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHFyMDF3dGRrazhkODRiYTY2MmR5ZGprOGkxYWw5ZnkzeXM5Z3phayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QLxybaWfZFt0sVKXb6/giphy.gif" alt="astro gif" />
  <small>Space Apps 2025</small>
</div>
""", unsafe_allow_html=True)






st.sidebar.title("🪐 ExoVision")
_current = st.session_state.get("page", ROUTES["home"])
idx = PAGES.index(_current) if _current in PAGES else 0
_selected = st.sidebar.radio("Secciones", PAGES, index=idx, label_visibility="visible")
if _selected != _current:
    st.session_state.page = _selected

page = st.session_state.get("page", ROUTES["home"])


# =========================
# HOME
# =========================
def render_home():
    HOME_CSS = """
    <style>
    .landing-card{
      position:relative; border-radius:24px; padding:28px; margin-top:6px;
      background:#ffffff; color:#0b1020;
      border:1px solid rgba(15,23,42,.06);
      box-shadow: 0 20px 60px rgba(0,0,0,.25);
    }
    .accent{
      position:absolute; right:24px; top:50%; transform:translateY(-50%);
      width:min(42vw,420px); aspect-ratio:1/1; border-radius:50%;
      background: radial-gradient(closest-side,#FFC764,#FF9D2E);
      filter: drop-shadow(0 10px 28px rgba(255,157,46,.45));
      opacity:.95;
    }
    .eyebrow{ font-weight:800; color:#FF9D2E; text-transform:uppercase; letter-spacing:.08em; }
    .hero-title{
      font-family:'Orbitron',sans-serif; line-height:1.05; letter-spacing:.5px;
      font-size:clamp(36px,5vw,56px); margin:6px 0 10px 0; color:#0b1020;
    }
    .tagline{ color:#334155; font-size:16px; margin:4px 0 16px 0 }
    .chip{
      display:inline-block; margin-top:8px; margin-right:8px; padding:6px 10px;
      border-radius:999px; background:#F3F4F6; color:#111827; font-size:.90rem;
      border:1px solid #E5E7EB;
    }
    .landing-card .stButton>button{
      height:48px; border-radius:12px; font-weight:800; font-size:16px;
      background:#FF9D2E; color:#0b1020; border:0; cursor:pointer;
      box-shadow:0 10px 20px rgba(255,157,46,.35);
    }
    .landing-card .stButton>button:hover{
      transform: translateY(-1px); box-shadow:0 14px 28px rgba(255,157,46,.45);
    }
    .art-wrap{ position:relative; height:360px; display:grid; place-items:center; }
    .art-wrap img{ position:relative; z-index:2; width:100%; max-width:520px; object-fit:contain; }
    .cta-title{
      text-align:center; margin-top:6px; font-weight:800; color:#0b1020; letter-spacing:.2px;
    }
    </style>
    """
    html_embed(HOME_CSS, height=0)

    st.markdown('<div class="landing-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.05, 1], vertical_alignment="center")

    with col1:
        st.markdown('<div class="eyebrow">Space Apps 2025</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">ExoVision<br/>hunting exoplanets with AI</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="tagline">Learn about exoplanets in minutes, have fun playing, and predict whether a signal is a <b>planet</b> or a <b>non-planet</b>.'
            'A useful tool for astronomers, researchers, and even beginners looking to learn more about the subject.</p>',
            unsafe_allow_html=True
        )

        # --- CTAs con títulos visibles y tooltip ---
        st.markdown("#### Explore")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.button("Learn", use_container_width=True,
                      help="Transit method explained easily",
                      on_click=goto_page, args=(ROUTES["learn"],))
            

        with c2:
            st.button("Predict", use_container_width=True,
                      help="Predict CONFIRMED vs FALSE POSITIVE",
                      on_click=goto_page, args=(ROUTES["predict"],))
            

        with c3:
            st.button("Play", use_container_width=True,
                      help="Mini-game: PLANET or NO PLANET?",
                      on_click=goto_page, args=(ROUTES["game"],))
            

        with c4:
            st.button("Chat", use_container_width=True,
                      help="Talk to ExoCimarron",
                      on_click=goto_page, args=(ROUTES["chat"],))
            

       

    with col2:
        st.markdown('<div class="art-wrap"><div class="accent"></div></div>', unsafe_allow_html=True)
        show_img(IMAGES.get("astro_gif", IMAGES.get("kepler")), caption=None)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CHAT
# =========================
def render_chat():
    st.title(f"💬 Chat — {BRAND}")
     
    SYSTEM_MSG = (
        """
        You are “ExoCimarron”, a friendly, expert guide on NASA, astronomy/astrophysics, space exploration, and ML/DL models for exoplanet detection. ALWAYS respond in neutral, clear, and concise Spanish (default: 4–6 sentences), beginning your messages with “ExoCimarron: ”.

GOAL
- Explain NASA concepts (missions, instruments, programs), space science (planets, stars, galaxies), and ML/DL pipelines applied to light curves and catalogs (Kepler, K2, TESS, JWST, HST, Roman, Gaia).
- Provide useful and actionable answers for students and judges: ideas, steps, metrics, and shortcode when appropriate.

STYLE
- Didactic and direct; use simple analogies without losing rigor.
- When using simple formulas or relationships, include them in concise LaTeX.
- If the user asks for "make it technical" or "expert mode," provide more in-depth answers (sections, equations, concept references).
- If they ask for "code," prioritize Python (scikit-learn / PyTorch / TensorFlow) with small, commented, and reproducible snippets.

SCOPE AND CONTENT
- NASA: Explain objectives, typical instruments (photometry, spectroscopy, coronagraphy), mission examples (Kepler/TESS for transits, JWST for spectra, HST, Roman, Gaia), and data products (PDCSAP curves, BJD times, catalogs, calibration levels).
- Exoplanets: Transit method, radial velocity, direct imaging, microlensing; signals and false positives (eclipsing binaries, instrumental noise, centroid shift).
- ML/DL for exoplanets:
* Preprocessing: detrend/flatten, normalization, phase folding, sliding windows, balancing.
* Tabular features: depth, duration, period, SNR, impact parameter, odd-even, secondary, out-of-transit statistics.
* Classical models: Logistic Regression, SVM, Random Forest, XGBoost; k-fold validation; metrics (Accuracy, F1, ROC-AUC, PR-AUC).
* DL: 1D CNN for curves, LSTM/GRU, Lightweight Transformers; regularization and early stopping.
* Typical 6-step pipeline: (1) ingestion/cleaning → (2) feature or tensor engineering → (3) stratified split → (4) training with hyperparameter search → (5) evaluation/ablation → (6) interpretation (importances/Grad-CAM) and thresholds.
- When the user asks for "steps" or "pipeline", respond with a short and clear numbered list.

RULES
- Don't fabricate specifics (exact numbers or mission results) if you're unsure; say "I'm not sure" and suggest how to verify.
- Don't include links; if you mention sources, name them in text (e.g., "NASA Exoplanet Archive," "Jenkins et al. (Kepler)") without URLs.
- Maintain the context of the chat and avoid repeating previously given definitions unless the user requests it.
- Be respectful, avoid unnecessary jargon, and don't share sensitive information.

USEFUL FORMATS
- "5-point summary" when the user requests a summary.
- "Tutorial mode": numbered steps + code snippet + recommended metric.
- Short formulas when they add value, for example: depth ≈ (Rp/R★)^2, duty ≈ duration/period.

RESPONSE PALETTES (user keyword switches)
- "short" → 2–3 sentences.
- "expert/advanced" → sections + equations + assumptions.
- "code" → minimal reproducible Python snippet.
- "example" → concrete case with plausible numbers (indicating that they are examples).

If a request is ambiguous, assume the most useful interpretation and make it explicit in an initial line ("Assumed interpretation: ...").

        """
        )

# Initial state
    if "chat_msgs" not in st.session_state or st.session_state.chat_msgs is None:
        st.session_state.chat_msgs = [{"role": "system", "content": SYSTEM_MSG}]

    # Ollama Config
    HOST   = os.environ.get("EXOCIM_OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    MODEL  = os.environ.get("EXOCIM_MODEL", "gemma3:latest")
    TEMP   = float(os.environ.get("EXOCIM_TEMP", "0.3"))
    MAXTOK = int(float(os.environ.get("EXOCIM_MAXTOK", "512")))

    # Reuse HTTP connection
    if "http" not in st.session_state:
        st.session_state.http = requests.Session()

    def _format_asst(md_text: str) -> str:
        msg = md_text.strip()
        if msg.lower().startswith("exocimarron:"):
            body = msg.split(":", 1)[1].strip()
            return f"**ExoCimarron:** {body}"
        return f"**ExoCimarron:** {msg}"

    def stream_ollama(messages):
        payload = {
            "model": MODEL,
            "messages": messages,
            "stream": True,
            "options": {"temperature": TEMP, "num_predict": MAXTOK},
        }
        with st.session_state.http.post(f"{HOST}/api/chat", json=payload, stream=True, timeout=600) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
                if data.get("done"):
                    break

    # Suggestions (chips) only if there's no user history
    if len(st.session_state.chat_msgs) == 1:
        st.markdown("""
        <div class="block">
          <h4 style="margin:0 0 6px 0;">Start the conversation - *the chatbot won't work if you don't install the package - (See Readme)*</h4>
          <p style="margin:0 0 8px 0; color:#a6c3db">Tap a suggestion:</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("What is an exoplanet?"):
                st.session_state._chip_prompt = "What is an exoplanet? Explain it to me simply."
            if st.button("Could there be life out there?"):
                st.session_state._chip_prompt = "Do you think there could be life on exoplanets? Explain it to me simply."
        with c2:
            if st.button("What's the point of searching for them?"):
                st.session_state._chip_prompt = "What's the point of searching for exoplanets? Give me 3 reasons."
            if st.button("Fun fact"):
                st.session_state._chip_prompt = "Give me a fun fact about exoplanets."
        with c3:
            if st.button("What was the Kepler mission?"):
                st.session_state._chip_prompt = "What was the Kepler mission and why was it important?"
            if st.button("How do we find them?"):
                st.session_state._chip_prompt = "How do we find exoplanets? Give me an easy explanation."

    # Render history (before input)
    for m in st.session_state.chat_msgs[1:]:
        if m["role"] == "user":
            with st.chat_message("user", avatar="🧑‍🚀"):
                st.markdown(m["content"])
        elif m["role"] == "assistant":
            with st.chat_message("assistant", avatar="🐏"):
                st.markdown(_format_asst(m["content"]))

    # Input bar ALWAYS visible
    chip_prompt = st.session_state.pop("_chip_prompt", None)
    typed_text  = st.chat_input("Write to ExoCimarron…", key="chatbox")
    user_text   = chip_prompt or typed_text

    if user_text:
        # user turn
        st.session_state.chat_msgs.append({"role": "user", "content": user_text})
        with st.chat_message("user", avatar="🧑‍🚀"):
            st.markdown(user_text)

        # assistant turn (stream)
        with st.chat_message("assistant", avatar="🐏"):
            placeholder = st.empty()
            full = ""
            try:
                for token in stream_ollama(st.session_state.chat_msgs):
                    full += token
                    placeholder.markdown(_format_asst(full) + "▌")
            except Exception:
                full = ("ExoCimarron: ⚠️ Could not connect to the local engine. "
                        "Verify that Ollama is running on 11434 and that the model is loaded.")
                placeholder.markdown(_format_asst(full))
            else:
                placeholder.markdown(_format_asst(full))

        st.session_state.chat_msgs.append({"role": "assistant", "content": full})
        st.stop()   # prevents full rerender





# =========================
# INFO — Método de tránsito
# =========================
def render_info():
    st.title("Learn — More")
    tab1, tab2 = st.tabs(["Concept", "Simulator"])

    with tab1:
        # Section 1: Basic concept
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("""
            An **exoplanet** is a planet that **orbits another star** outside the Solar System.  
            The most successful method to detect them is the **transit method**: when the planet passes
            in front of its star, the brightness drops a little bit and in a **periodic** manner.

            **What we measure:**
            - **Depth**: how large the planet is relative to the star.
            """)
            st.latex(r"\text{depth} \approx \left(\frac{R_p}{R_\star}\right)^2")
            st.markdown("""
            * **Duration:** Associated with the **width of the valley** in the light curve. It depends on the planet's orbital velocity and the size of the star.
            * **Period:** The **periodic repetition** of the same pattern indicates the **time it takes the planet to complete one full orbit** around its star.
            """)
        with c2:
            show_img(IMAGES["kepler"], "Kepler Mission (NASA)")

        st.markdown("---")

        # Section 2: Transit method (now in Concept)
        st.subheader("Transit method")
        c1, c2 = st.columns(2)
        with c1:
            show_img("https://i.giphy.com/coBd3RjR8tGGh6UOOm.webp", "Transit animation")
        with c2:
            st.markdown("""
            When an exoplanet passes in front of its star (from our point of view), it blocks a small fraction of its light. This is observed as a periodic decrease in the luminous flux recorded in the light curve.
            * **(A) Out of transit:** The planet is not in front of the star. The observed light flux is **constant and normalized to ~1.0**
            * **(B) Ingress:** The planet begins to pass in front of the stellar disk. A **gradual drop** in light flux is observed, as the planet starts to block part of the stellar surface.
            * **(C) Minimum (mid-transit):** The planet is **aligned with the center of the stellar disk** (if the trajectory is central). This point indicates the deepest part of the "valley" in the light curve.
            * **(D) Egress:** The planet begins to exit the stellar disk. The amount of blocked light **gradually decreases**, and the flux **returns to its normal level (~1.0)** when the transit ends.
        
            """)
    

    with tab2:
        st.subheader("Play with a synthetic transit")
        c = st.columns(6)
        P_days       = c[0].slider("Period (days)",            0.5, 500.0, 20.0, 0.5)
        duration_h   = c[1].slider("Duration (hours)",          0.2,  30.0,  5.0, 0.1)
        k_rprs       = c[2].slider("Relative size rp/rs",     0.005,0.20, 0.05, 0.001, help="Planet radius / star radius")
        b_impact     = c[3].slider("Impact (b)",               0.0,   1.0,  0.20, 0.01, help="0 centered, 1 grazing")
        noise_sigma  = c[4].slider("Noise σ (rel.)",            0.0,   0.01, 0.002, 0.0005)
        vshape       = c[5].slider("Shape U ↔ V",               0.0,   0.60, 0.20, 0.05, help="0 = smooth U, 0.6 = sharp V")

        star_cols = st.columns(2)
        center_phase= star_cols[0].slider("Transit center (phase)", 0.1, 0.9, 0.5, 0.01)
        show_marks  = star_cols[1].checkbox("Mark ingress/egress", True)

        def transit_curve(n=900, depth=0.01, width=0.08, center=0.5, vshape=0.2, noise=0.0):
            x = np.linspace(0, 1, n)
            y = np.ones_like(x)
            ingress, egress = center - width/2, center + width/2
            for i, xi in enumerate(x):
                if ingress <= xi <= egress:
                    frac = abs((xi-center)/(width/2))
                    shape = (1 - vshape*frac)  # U ↔ V
                    y[i] = 1.0 - depth*shape
            if noise > 0: y += np.random.normal(0.0, noise, size=n)
            return x, y, ingress, egress

        duty = (duration_h / (P_days * 24.0))
        depth = k_rprs**2
        x, y, ingress, egress = transit_curve(depth=depth, width=duty, center=center_phase, vshape=vshape, noise=noise_sigma)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(width=2, color="#8bd7ff")))
        if show_marks:
            fig.add_vline(x=float(ingress), line_width=1, line_dash="dash", line_color="#ffaa00")
            fig.add_vline(x=float(center_phase), line_width=1, line_dash="dot",  line_color="#ff66aa")
            fig.add_vline(x=float(egress),  line_width=1, line_dash="dash", line_color="#ffaa00")
            fig.add_annotation(x=center_phase, y=min(y), text="Center", showarrow=False, yshift=-10, font=dict(color="#ff66aa"))
        fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10,r=10,t=30,b=10),
                          xaxis_title="Orbital phase (0–1)", yaxis_title="Relative flux", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        depth_ppm = depth * 1e6
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Depth", f"{depth_ppm:,.0f} ppm")
        m2.metric("rp/rs", f"{k_rprs:.3f}")
        m3.metric("Duration", f"{duration_h:.2f} h")
        m4.metric("Duty cycle", f"{duty:.3f}")
        m5, m6 = st.columns(2)
        m5.metric("Planet radius", f"{k_rprs:.1f} R⊕")
        m6.metric("Impact (b)", f"{b_impact:.2f}")

# =========================
# GAME — Caza exoplanetas
# =========================
def render_game():
    st.title("🎮 Play — PLANET or NOT PLANET?")
    st.caption("Look at the light curve and choose. Immediate feedback.")

    cset = st.columns(5)
    difficulty = cset[0].selectbox("Difficulty", ["Easy","Medium","Hard"], index=1)
    n_points   = cset[1].number_input("Points", 200, 3000, 600, 100)
    rounds     = cset[2].slider("Rounds", 3, 20, 7, 1)
    show_hints = cset[3].checkbox("Show hints", True)
    show_truth = cset[4].checkbox("Show solution on failure", True)
    noise = {"Easy":0.002, "Medium":0.004, "Hard":0.008}[difficulty]

    if "g_idx" not in st.session_state: st.session_state.g_idx=0
    if "g_score" not in st.session_state: st.session_state.g_score=0
    if "g_truth" not in st.session_state: st.session_state.g_truth=None
    if "g_xy" not in st.session_state: st.session_state.g_xy=None

    def synth_transit(n=600, depth=0.004, width=0.08, center=0.5, vshape=0.0, noise=0.003):
        x = np.linspace(0,1,n); y = np.ones_like(x)
        ingress, egress = center-width/2, center+width/2
        for i, xi in enumerate(x):
            if ingress <= xi <= egress:
                frac = abs((xi-center)/(width/2))
                y[i] = 1.0 - depth*(1.0 - 0.20*vshape*frac)
        y += np.random.normal(0, noise, size=n); return x,y

    def synth_nonplanet(n=600, noise=0.003):
        x = np.linspace(0,1,n)
        y = 1.0 + 0.02*np.sin(2*np.pi*x*3)
        if np.random.rand()<0.6:
            c = np.random.uniform(0.4,0.6); w = np.random.uniform(0.02,0.04); d = np.random.uniform(0.01,0.03)
            L,R = c-w/2, c+w/2
            for i, xi in enumerate(x):
                if L <= xi <= R:
                    frac = abs((xi-c)/(w/2))
                    y[i] -= d*(1.0 - 0.30*frac)
        y += np.random.normal(0, noise*1.2, size=n); return x,y

    def new_round():
        is_planet = bool(np.random.rand()<0.5)
        if is_planet:
            depth = np.random.uniform(0.0006,0.008)
            width = np.random.uniform(0.05,0.12)
            vshape = np.random.uniform(0.0,0.25)
            x,y = synth_transit(n_points, depth, width, 0.5, vshape, noise)
        else:
            x,y = synth_nonplanet(n_points, noise)
        st.session_state.g_truth = "PLANET" if is_planet else "NOT PLANET"
        st.session_state.g_xy = (x,y)

    if st.session_state.g_xy is None: new_round()

    x,y = st.session_state.g_xy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(width=2, color="#8bd7ff")))
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=28,b=10),
                      xaxis_title="Orbital phase (0–1)", yaxis_title="Relative flux", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    if show_hints:
        st.info("**Hints:** real transits are usually deep (ppm), symmetric, with **U** shape; false positives often show sharp **V** dips or modulation around.")

    b1,b2,b3 = st.columns(3)
    guess = None
    if b1.button("🪐 It's a PLANET!", use_container_width=True): guess="PLANET"
    if b2.button("🛰️ NOT PLANET", use_container_width=True):  guess="NOT PLANET"
    if b3.button("🔁 New signal", use_container_width=True): new_round()

    if guess is not None:
        truth = st.session_state.g_truth
        if guess == truth:
            st.success("✅ Correct! +1 point")
            st.session_state.g_score += 1
        else:
            st.error(f"❌ Incorrect. It was **{truth}**")
            if show_truth:
                msg = "• Smooth and symmetric dip → typical transit." if truth=="PLANET" else "• Very sharp/modulated dip → not a planet."
                st.caption(f"Explanation: {msg}")
        st.session_state.g_idx += 1
        if st.session_state.g_idx >= rounds:
            st.subheader("🏁 Final result")
            st.metric("Score", f"{st.session_state.g_score}/{rounds}")
            if st.button("🧹 Restart"):
                st.session_state.g_idx=0; st.session_state.g_score=0
            new_round()
        else:
            new_round()



# =========================
# PREDICTOR — Leaderboard + selector + PREDECIR CON IA (arriba, con GIF)
# =========================
def render_predictor():
    import os, json, joblib
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit as st

    st.title(f"{BRAND}: Prediction — CONFIRMED vs FALSE POSITIVE")

    MODELS_DIR   = "models"
    METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")  # precomputed metrics

    # -------- Helpers
    def list_models():
        if not os.path.isdir(MODELS_DIR):
            return []
        return sorted([os.path.splitext(fn)[0] for fn in os.listdir(MODELS_DIR) if fn.lower().endswith(".pkl")])

    @st.cache_resource(show_spinner=False)
    def load_model(model_name: str):
        return joblib.load(os.path.join(MODELS_DIR, f"{model_name}.pkl"))

    @st.cache_resource(show_spinner=False)
    def load_features():
        try:
            with open(os.path.join(MODELS_DIR, "features.json"), "r") as f:
                return json.load(f)
        except Exception:
            return None

    @st.cache_data(show_spinner=False)
    def load_metrics():
        try:
            with open(METRICS_PATH, "r") as f:
                return json.load(f)  # dict: {model: {"accuracy": 0.xx, "f1": ...}}
        except Exception:
            return {}

    # -------- Detect models and metrics
    available = list_models()
    if not available:
        st.error("No models found in `./models`. Upload your *.pkl files to that folder.")
        st.stop()

    metrics = load_metrics()
    feats   = load_features()

    # -------- Leaderboard (table + bars)
    st.subheader("Model leaderboard")
    rows = []
    for m in available:
        acc = metrics.get(m, {}).get("accuracy", None)
        rows.append({"Model": m, "Accuracy": acc})
    leaderboard = pd.DataFrame(rows).sort_values(by="Accuracy", ascending=False, na_position="last")

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.dataframe(leaderboard, use_container_width=True)
    with c2:
        acc_pct = (leaderboard["Accuracy"].fillna(0) * 100).round(1)
        fig = go.Figure(go.Bar(
            x=leaderboard["Model"],
            y=acc_pct,
            text=[f"{v:.1f}%" for v in acc_pct],
            textposition="outside",
            marker=dict(
                color=["#60A5FA", "#34D399", "#A78BFA", "#F59E0B", "#F472B6", "#7DD3FC"][:len(acc_pct)],
                line=dict(color="rgba(255,255,255,0.35)", width=1.2)
            )
        ))
        ymax = float(acc_pct.max() if len(acc_pct) else 100)
        fig.update_layout(
            template="plotly_dark",
            height=340,
            margin=dict(l=30, r=50, t=30, b=100),
            yaxis_title="Accuracy (%)",
            xaxis_title=""
        )
        fig.update_xaxes(tickangle=-25, automargin=True)
        fig.update_yaxes(range=[0, ymax * 1.15], automargin=True)
        fig.update_traces(cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

    # -------- Selector + Accuracy + CTA PREDICT (top)
    recommended   = leaderboard.iloc[0]["Model"] if len(leaderboard) else available[0]
    use_rec       = st.toggle("Use recommended automatically", value=True, help="Select the best by Accuracy")
    default_index = available.index(recommended) if (use_rec and recommended in available) else 0

    top_l, top_m, top_r = st.columns([1.2, 0.8, 1.4])
    with top_l:
        model_name = st.selectbox("Active model", available, index=default_index, help="Model for banner and gauge")
    with top_m:
        acc_show = metrics.get(model_name, {}).get("accuracy", None)
        if acc_show is not None:
            st.metric("Accuracy (val/test)", f"{acc_show*100:.2f}%")
        else:
            st.info("Accuracy: N/A")

    # --- CTA with space GIF (nice and big)
    CTA_GIF = "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMzd3c201aDZ6djdoa2FoZWZ2Y2t3ZnJueWR5c2duMXNmeGVpNDdhMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Wkcw6SzOtaSxG/giphy.gif"
    with top_r:
        st.markdown(
            f"""
            <style>
            .primary-cta .stButton > button {{
                background: linear-gradient(135deg,#ff6a3d 0%, #ff2a74 45%, #7136ff 100%);
                color:#fff; font-weight:900; font-size:18px; letter-spacing:.6px;
                border:0; border-radius:14px; width:100%;
                padding:22px 24px 22px 86px;
                box-shadow:0 16px 40px rgba(255,64,125,.35);
                transition:transform .05s ease-in, box-shadow .2s ease;
                background-image:url('{CTA_GIF}');
                background-size:46px 46px; background-repeat:no-repeat; background-position:22px center;
            }}
            .primary-cta .stButton > button:hover {{
                transform: translateY(-1px);
                box-shadow:0 22px 60px rgba(255,64,125,.45);
            }}
            .primary-cta .stButton > button:active {{
                transform: translateY(0px) scale(.995);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="primary-cta">', unsafe_allow_html=True)
        do_predict = st.button("PREDICT WITH AI", use_container_width=True, key="cta_predict")
        st.markdown('</div>', unsafe_allow_html=True)

    st.caption("Adjust values or use a preset. Typical Kepler ranges.")

    # -------- Presets (without Hot Jupiter)
    presets = {
        "🌍 Earth-like": {
            "koi_period": 365.0, "koi_duration": 10.0, "koi_depth": 84.0, "koi_model_snr": 12.0,
            "koi_impact": 0.2, "koi_time0bk": 900.0, "koi_steff": 5750.0, "koi_slogg": 4.45,
            "koi_srad": 1.0, "koi_smet": 0.0, "koi_kepmag": 14.0, "duty_cycle": 10.0/(365*24), "rp_rs": 0.0091
        },
        "🔵 Neptune-like": {
            "koi_period": 30.0, "koi_duration": 6.0, "koi_depth": 2000.0, "koi_model_snr": 25.0,
            "koi_impact": 0.3, "koi_time0bk": 700.0, "koi_steff": 5400.0, "koi_slogg": 4.4,
            "koi_srad": 1.0, "koi_smet": -0.1, "koi_kepmag": 13.5, "duty_cycle": 6.0/(30*24), "rp_rs": 0.035
        }
    }
    pc = st.columns(len(presets))
    for (i, (label, values)) in enumerate(presets.items()):
        if pc[i].button(label, use_container_width=True, key=f"preset_{i}"):
            st.session_state.predictor_values.update(values)
            st.toast(f"Preset applied: {label}")

    # -------- Sliders
    slider_spec = [
        ("Orbital period (days)",            "koi_period",     0.5,   500.0,  20.0,   0.1,  "Period between transits."),
        ("Transit duration (hours)",     "koi_duration",   0.2,    30.0,   5.0,   0.1,  "Time the transit lasts."),
        ("Transit depth (ppm)",    "koi_depth",     20.0, 50000.0, 800.0,  10.0,  "Flux drop (ppm)."),
        ("Transit model SNR",        "koi_model_snr",  1.0,   300.0,  20.0,   0.5,  "Signal-to-noise ratio."),
        ("Impact parameter (b)",          "koi_impact",     0.0,     1.2,   0.3,   0.01, "0 centered, 1 grazing."),
        ("Transit epoch (BKJD)",         "koi_time0bk",  100.0,  2000.0, 900.0,   1.0,  "Barycentric Kepler JD – 2454833."),
        ("Stellar effective temperature (K)",  "koi_steff",   3000.0, 10000.0, 5700.0, 10.0,  "Star's Teff."),
        ("Stellar log g (cgs)",               "koi_slogg",      3.0,     5.5,   4.4,   0.01, "Surface gravity."),
        ("Stellar radius (R☉)",                "koi_srad",       0.1,    20.0,   1.0,   0.01, "In solar radii."),
        ("Metallicity [Fe/H] (dex)",         "koi_smet",      -1.0,     0.5,   0.0,   0.01, "Relative abundance."),
        ("Kepler magnitude",                   "koi_kepmag",     9.0,    17.5,  14.0,   0.1,  "Brightness in Kepler band."),
        ("Duty cycle (duration/period)",     "duty_cycle",     0.0,     0.2,   0.01,  0.001,"Fraction of time in transit."),
        ("Radius ratio rp/rs",             "rp_rs",          0.005,   0.20,  0.05,  0.001,"~√(depth)."),
    ]
    desired_order       = (feats if feats else [s[1] for s in slider_spec])
    spec_by_name        = {s[1]: s for s in slider_spec}
    slider_names_ordered= [c for c in desired_order if c in spec_by_name]

    values = {}
    for i in range(0, len(slider_names_ordered), 2):
        cA, cB = st.columns(2)
        for col, name in zip((cA, cB), slider_names_ordered[i:i+2]):
            label, key, vmin, vmax, vdef, step, help_ = spec_by_name[name]
            default = st.session_state.predictor_values.get(key, vdef)
            with col:
                v = st.slider(label, float(vmin), float(vmax), float(default), float(step), help=help_, key=f"sl_{key}")
                values[key] = v

    # -------- Build X with correct order
    X = pd.DataFrame([[values.get(c, 0.0) for c in slider_names_ordered]], columns=slider_names_ordered)

    def align_X_for(model):
        if hasattr(model, "feature_names_in_"):
            Z = X.copy()
            for miss in model.feature_names_in_:
                if miss not in Z.columns:
                    Z[miss] = 0.0
            return Z[model.feature_names_in_]
        elif feats:
            Z = X.copy()
            for miss in feats:
                if miss not in Z.columns:
                    Z[miss] = 0.0
            return Z[feats]
        return X

    st.markdown("---")

    # ====== ACTION: PREDICT WITH AI ======
    if do_predict:
        rows_pred = []
        for m in available:
            mdl = load_model(m)
            Xi  = align_X_for(mdl)
            yhat = int(mdl.predict(Xi)[0])
            rows_pred.append({
                "Model": m,
                "Prediction": "CONFIRMED" if yhat==1 else "FALSE POSITIVE",
                "Accuracy(ref)": (None if metrics.get(m, {}).get("accuracy") is None else f"{metrics[m]['accuracy']*100:.2f}%")
            })

        # Results table
        dfp = pd.DataFrame(rows_pred)
        st.subheader("AI results for this input")
        st.dataframe(dfp, use_container_width=True)

        # Message + gauge using ONLY Accuracy (ref)
        mdl_sel  = load_model(model_name)
        Xi_sel   = align_X_for(mdl_sel)
        yhat_sel = int(mdl_sel.predict(Xi_sel)[0])
        label_sel= "CONFIRMED" if yhat_sel == 1 else "FALSE POSITIVE"
        acc_show = metrics.get(model_name, {}).get("accuracy", None)

        msg = f"ExoCimarron ({model_name}) says: **{label_sel}** · " + \
              (f"Accuracy(ref) ≈ {acc_show*100:.2f}%" if acc_show is not None else "Accuracy(ref): N/A")

        if yhat_sel == 1:
            st.success(msg, icon="✅")
            bar_color = "#22c55e"  # green
        else:
            st.error(msg, icon="❌")
            bar_color = "#ef4444"  # red

        if acc_show is not None:
            gfig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=acc_show*100,
                number={"suffix":"%"},
                gauge={"axis":{"range":[0,100]}, "bar":{"thickness":0.35, "color": bar_color}},
                domain={"x":[0,1],"y":[0,1]}
            ))
            gfig.update_layout(template="plotly_dark", height=280, margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(gfig, use_container_width=True)

    # Tips
    with st.expander("Quick tips"):
        st.write("""
        - Use the leaderboard to compare models without changing views.
        - The table shows the prediction from **all** models and their **Accuracy(ref)** (valid/test).
        - The banner and gauge use the **active model** from the selector above.
        """)




# =========================
# ABOUT
# =========================
def render_about():
    st.title("About the solution")
    st.markdown(f"""
    <div class="block">
      <p><b>ExoVision</b> combines science, gaming and AI to explain the transit method in an accessible way.</p>
      <p>Main features:</p>
      <ul>
        <li>Educational chat with local model</li>
        <li>Interactive light curve game</li>
        <li>Planetary transit simulator</li>
        <li>Binary predictor (CONFIRMED vs FALSE POSITIVE) based on multiple models</li>
      </ul>
      <p>Challenge: <b>A World Away (Hunting for Exoplanets with AI)</b> NASA Space Apps 2025.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Development timeline")

    timeline_data = [
        {
            "date": "2025-10-04",
            "phase": "Project creation and literature review",
            "description": "Research on the transit method, analysis of the Kepler dataset and study of classification algorithms. The Kepler dataset turned out to be the best alternative due to its quality, data volume and complete documentation.",
            "image": "research"
        },
        {
            "date": "2025-10-04",
            "phase": "Data Exploration",
            "description": "Data from each dataset, including Kepler, was explored in order to understand the data to be used for the model development.",
            "image": "dataset"
        },
        {
            "date": "2025-10-04",
            "phase": "AI model development",
            "description": "Training and validation of multiple machine learning models. Gradient Boost proved to be the best alternative due to its ability to handle unbalanced data and its robustness against noisy features typical of astronomical signals.",
            "image": "ai_model"
        },
        {
            "date": "2025-10-04",
            "phase": "Chatbot development",
            "description": "Implementation of the conversational system using Ollama with Gemma3 model. Integration of specific knowledge about exoplanets and the transit method through specialized prompts.",
            "image": "chatbot"
        },
        {
            "date": "2025-10-04",
            "phase": "Simulator and game",
            "description": "Construction of the interactive planetary transit simulator with realistic synthetic curves. Development of the educational game to identify planetary signals vs false positives.",
            "image": "simulator"
        },
        {
            "date": "2025-10-04",
            "phase": "Testing and optimization",
            "description": "Exhaustive testing of each module, performance optimization, validation of predictions against known data and refinement of the user interface.",
            "image": "testing"
        },
        {
            "date": "2025-10-05",
            "phase": "Final integration",
            "description": "Unification of all components into a coherent application, final design adjustments and preparation of technical documentation.",
            "image": "team"
        },
        {
            "date": "2025-10-05",
            "phase": "Presentation",
            "description": "Deployment of the complete MVP application, preparation of demonstration materials and final documentation for Space Apps Challenge judges.",
            "image": "presentation"
        }
    ]

    st.markdown("""
    <style>
    /* Main container for each timeline block */
    .timeline-row {
        display: flex;
        align-items: center;
        margin-bottom: 40px;
    }
    /* Image column */
    .img-container {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    /* Image */
    img.timeline {
        width: 260px;
        height: auto;
        border-radius: 14px;
        object-fit: contain;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    }
    /* Text column */
    .text-container {
        flex: 2;
        padding-left: 20px;
    }
    /* Text block */
    .block {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main timeline loop
    for item in timeline_data:
        st.markdown(f"""
        <div class="timeline-row">
            <div class="img-container">
                <img class="timeline" src="{IMAGES[item['image']]}" />
            </div>
            <div class="text-container">
                <div class="block">
                    <p style="color: #FF9D2E; font-weight: 800; margin: 0 0 4px 0;">{item["date"]}</p>
                    <h4 style="margin: 0 0 8px 0;">{item["phase"]}</h4>
                    <p style="margin: 0; color: #9bb3c8;">{item["description"]}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Gallery")
    g1, g2, g3 = st.columns(3)
    with g1: show_img(IMAGES["nasa_logo"], caption="NASA")
    with g2: show_img(IMAGES["kepler"], caption="Kepler")
    with g3: show_img(IMAGES["transit"], caption="Transit (ESA)")
    
    st.markdown("---")
    
    st.markdown("### References")
    
    st.markdown("#### Scientific Literature")
    st.markdown("""
    - Alik, A., Moster, B. P., & Obermeier, C. (2022). Exoplanet detection using machine learning. *Monthly Notices of the Royal Astronomical Society*, 513(4), 5505–5516. https://doi.org/10.1093/mnras/stab3692
    
    - Luz, T. S. F., Braga, R. A. S., & Ribeiro, E. R. (2024). Assessment of ensemble-based machine learning algorithms for exoplanet identification. *Electronics*, 13(19), 3950. https://doi.org/10.3390/electronics13193950
    """)
    
    st.markdown("#### Data Sources and Visual Resources")
    
    with st.expander("View complete reference list"):
        st.markdown("""
        **Images and Data:**
        
        - ESA. (2003). Planet transit [Illustration]. European Space Agency. https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2003/06/planet_transit/9798645-3-eng-GB/Planet_transit_pillars.jpg
        
        - HowStuffWorks. (n.d.). Exoplanets [Photography]. https://media.hswstatic.com/eyJidWNrZXQiOiJjb250ZW50Lmhzd3N0YXRpYy5jb20iLCJrZXkiOiJnaWZcL2V4b3BsYW5ldHMtMS5qcGciLCJlZGl0cyI6eyJyZXNpemUiOnsid2lkdGgiOjgyOH0sInRvRm9ybWF0IjoiYXZpZiJ9fQ==
        
        - NASA. (n.d.). NASA logo [Logo]. SeekLogo. https://images.seeklogo.com/logo-png/9/1/nasa-logo-png_seeklogo-97034.png
        
        - NASA. (n.d.). Webb telescope transit animation [GIF]. Giphy. https://giphy.com/gifs/nasa-webb-jwst-nasawebb-coBd3RjR8tGGh6UOOm
        
        - NASA Exoplanet Science Institute. (2024). NASA Exoplanet Archive: Kepler Objects of Interest [Dataset]. California Institute of Technology. https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=cumulative
        
        - NASA/Ames/JPL-Caltech. (2014). Kepler Mission [Photography]. NASA Image and Video Library. https://images-assets.nasa.gov/image/PIA18904/PIA18904~large.jpg
        
        **Animations:**
        
        - Giphy. (n.d.). AI and machine learning animation [GIF]. https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeDJ5bDU3bmxqYThzOThwa2I3M21rY2lnZDhsNm42b3YxMGdsNzRwMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LR5ZBwZHv02lmpVoEU/giphy.gif
        
        - Giphy. (n.d.). Astronomy animation [GIF]. https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDBnNDF6Zmh3anF3bGRrMjRya2Q3M2hibXZjNGJ3NGtnZWh0YThmMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlO4V8iCRME3i0g/giphy.gif
        
        - Giphy. (n.d.). Chatbot animation [GIF]. https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWE1MzRyM2g3ZG50dnZodzYyNmhhZmt5ZGYwOHJvanlnZmw0dGhxbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S60CrN9iMxFlyp7uM8/giphy.gif
        
        - Giphy. (n.d.). Presentation animation [GIF]. https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExam83bzgxZTd6aHpuYmQxczloeWdhaHoxbzczOWVyOWI2ZDR0MWEycyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/U3dIoNBOyfTkA/giphy.gif
        
        - Giphy. (n.d.). Research animation [GIF]. https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2VyOTJsdGdibTJicGIwdm52YWV3dDJ5dndib20zN3Rxd2JpY2M2cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0GsNMsRwDKKMjiwIe5/giphy.gif
        
        - Giphy. (n.d.). Space simulation animation [GIF]. https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTZ1MWo4aTQwaDJkbXZnd2JnZjV2ZmtvaW83YmpmMzEyNzNncjJieiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hsubjoiDroLg4AYyUO/giphy.gif
        
        - Giphy. (n.d.). Teamwork animation [GIF]. https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExa24zZW53bGRsNjZobG9pdWlqbXcxbHdubHZqZTkyeWVxMHR5c3BoMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9yssegcqq1WDlPKdP4/giphy.gif
        
        - Giphy. (n.d.). Testing and validation animation [GIF]. https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjhremVrb3JybnA4eDU0em43eXd5cHc5bHV4OWRqdmFvdHprbXV2eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gw3IWyGkC0rsazTi/giphy.gif
        """)
# =========================
# ROUTER
# =========================
if page == ROUTES["home"]:
    render_home()
elif page == ROUTES["learn"]:
    render_info()
elif page == ROUTES["predict"]:
    render_predictor()
elif page == ROUTES["game"]:
    render_game()
elif page == ROUTES["chat"]:
    render_chat()
elif page == ROUTES["about"]:
    render_about()
