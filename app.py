# app.py — ExoCimarron (Space Apps MVP) — versión completa y pulida para jueces
# Incluye: Landing "card blanca + acento", sidebar-botones, chat sin delay/duplicados,
# Info/Juego/Predictor, y CTAs con títulos visibles y tooltips.

import os, json, requests, joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit.components.v1 import html as html_embed

# =========================
# CONFIG / BRANDING
# =========================
BRAND = "ExoCimarron"
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
}

def show_img(src, caption=None):
    try:
        st.image(src, caption=caption, use_container_width=True)
    except Exception:
        st.info("No pude renderizar esta imagen directamente. Ábrela en nueva pestaña:")
        st.link_button("Abrir imagen", src)

# =========================
# GLOBAL THEME (oscuro elegante)
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
    "home":    "Inicio",
    "learn":   "Aprende Más",
    "predict": "Predice IA",
    "game":    "Juega ",
    "chat":    "Chatea con ExoCimarron",
    "about":   "Acerca del MVP",
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






st.sidebar.title("🪐 ExoCimarron")
_current = st.session_state.get("page", ROUTES["home"])
idx = PAGES.index(_current) if _current in PAGES else 0
_selected = st.sidebar.radio("Secciones", PAGES, index=idx, label_visibility="visible")
if _selected != _current:
    st.session_state.page = _selected

# 👇 AÑADE ESTAS DOS LÍNEAS
page = st.session_state.get("page", ROUTES["home"])


# =========================
# HOME (landing para jueces no técnicos)
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
        st.markdown('<h1 class="hero-title">Exo Cimarron<br/>hunting exoplanets with AI</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="tagline">Aprende en minutos sobre Exoplanetas, diviertete jugando y predice si una señal es <b>PLANETA</b> o <b>NO PLANETA</b>. '
            'Herramienta util para astronomos, investigadores e incluso principiantes queriendo aprender mas sobre el tema.</p>',
            unsafe_allow_html=True
        )

        # --- CTAs con títulos visibles y tooltip ---
        st.markdown("#### Explora")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.button("Aprende", use_container_width=True,
                      help="Método de tránsito explicado fácil",
                      on_click=goto_page, args=(ROUTES["learn"],))
            

        with c2:
            st.button("Predice", use_container_width=True,
                      help="Predice CONFIRMED vs FALSE POSITIVE",
                      on_click=goto_page, args=(ROUTES["predict"],))
            

        with c3:
            st.button("Juega", use_container_width=True,
                      help="Mini-juego: ¿PLANETA o NO PLANETA?",
                      on_click=goto_page, args=(ROUTES["game"],))
            

        with c4:
            st.button("Chat", use_container_width=True,
                      help="Habla con ExoCimarron",
                      on_click=goto_page, args=(ROUTES["chat"],))
            

       

    with col2:
        st.markdown('<div class="art-wrap"><div class="accent"></div></div>', unsafe_allow_html=True)
        show_img(IMAGES.get("astro_gif", IMAGES.get("kepler")), caption=None)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("**Dato:** Kepler ayudó a confirmar **+2,700** exoplanetas.", icon="✨")
    with f2:
        st.info("**Curiosidad:** algunos ‘Júpiter calientes’ orbitan en **~3 días**.", icon="🪐")
    with f3:
        st.info("**Tip:** un tránsito baja el brillo solo **unas ppm** (poquísimo).", icon="📉")



# =========================
# CHAT (fluido, sin rerun, sin "Limpiar chat" ni tip)
# =========================
def render_chat():
    st.title(f"💬 Chat — {BRAND}")
     
    SYSTEM_MSG = (
        """
        Eres “ExoCimarron”, un guía experto y amable sobre NASA, astronomía/astrofísica, exploración espacial y modelos de ML/DL para detección de exoplanetas. Responde SIEMPRE en español neutro, claro y conciso (por defecto 4–6 frases), comenzando tus mensajes con “ExoCimarron: ”.

OBJETIVO
- Explicar conceptos de NASA (misiones, instrumentos, programas), ciencia del espacio (planetas, estrellas, galaxias), y pipelines de ML/DL aplicados a curvas de luz y catálogos (Kepler, K2, TESS, JWST, HST, Roman, Gaia).
- Dar respuestas útiles y accionables para estudiantes y jurados: ideas, pasos, métricas, y código corto cuando sea apropiado.

ESTILO
- Didáctico y directo; usa analogías simples sin perder rigor.
- Cuando haya fórmulas o relaciones sencillas, inclúyelas en LaTeX breve.
- Si el usuario pide “hazlo técnico” o “modo experto”, responde con más profundidad (secciones, ecuaciones, referencias de conceptos).
- Si pide “código”, prioriza Python (scikit-learn / PyTorch / TensorFlow) con fragmentos pequeños, comentados y reproducibles.

ALCANCE Y CONTENIDO
- NASA: explica objetivos, instrumentos típicos (fotometría, espectroscopía, coronografía), ejemplos de misiones (Kepler/TESS para tránsitos, JWST para espectros, HST, Roman, Gaia), y productos de datos (curvas PDCSAP, tiempos BJD, catálogos, niveles de calibración).
- Exoplanetas: método de tránsito, velocidad radial, imágenes directas, microlente; señales y falsos positivos (binarias eclipsantes, ruido instrumental, centroid shift).
- ML/DL para exoplanetas:
  * Preprocesamiento: detrend/flatten, normalización, phase folding, ventanas deslizantes, balanceo.
  * Features tabulares: profundidad, duración, periodo, SNR, parámetro de impacto, “odd-even”, secundario, estadísticos del out-of-transit.
  * Modelos clásicos: Regresión Logística, SVM, RandomForest, XGBoost; validación k-fold; métricas (Accuracy, F1, ROC-AUC, PR-AUC).
  * DL: CNN 1D para curvas, LSTM/GRU, Transformers ligeros; regularización y early stopping.
  * Pipeline típico en 6 pasos: (1) ingestión/limpieza → (2) ingeniería de características o tensores → (3) split estratificado → (4) entrenamiento con búsqueda de hiperparámetros → (5) evaluación/ablation → (6) interpretación (importancias/Grad-CAM) y umbrales.
- Cuando el usuario pida “pasos” o “pipeline”, responde con lista numerada breve y clara.

REGLAS
- No inventes datos concretos (números exactos o resultados de misión) si no estás seguro; di “No estoy seguro” y sugiere cómo verificarlo.
- No pongas enlaces; si mencionas fuentes, nómbralas en texto (p. ej., “NASA Exoplanet Archive”, “Jenkins et al. (Kepler)”) sin URL.
- Mantén el contexto del chat y evita repetir definiciones ya dadas salvo que el usuario lo pida.
- Sé respetuoso, evita jerga innecesaria, y no compartas información sensible.

FORMATOS ÚTILES
- “Resumen en 5 puntos” cuando el usuario pida síntesis.
- “Modo tutorial”: pasos numerados + fragmento de código + métrica recomendada.
- Fórmula breve cuando aporte valor, por ejemplo: depth ≈ (Rp/R★)^2, duty ≈ duración/periodo.

PALETAS DE RESPUESTA (conmutadores por palabra clave del usuario)
- “corto” → 2–3 frases.
- “experto/avanzado” → secciones + ecuaciones + supuestos.
- “código” → snippet Python mínimo reproducible.
- “ejemplo” → caso concreto con números verosímiles (indicando que son de ejemplo).

Si una petición es ambigua, asume la interpretación más útil y explícitala en una línea inicial (“Interpretación asumida: …”).

        """
        )

    # Estado inicial
    if "chat_msgs" not in st.session_state or st.session_state.chat_msgs is None:
        st.session_state.chat_msgs = [{"role": "system", "content": SYSTEM_MSG}]

    # Config Ollama
    HOST   = os.environ.get("EXOCIM_OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    MODEL  = os.environ.get("EXOCIM_MODEL", "gemma3:latest")
    TEMP   = float(os.environ.get("EXOCIM_TEMP", "0.3"))
    MAXTOK = int(float(os.environ.get("EXOCIM_MAXTOK", "512")))

    # Reusar conexión HTTP
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

    # Sugerencias (chips) sólo si no hay historial de usuario
    if len(st.session_state.chat_msgs) == 1:
        st.markdown("""
        <div class="block">
          <h4 style="margin:0 0 6px 0;">Empieza la conversación</h4>
          <p style="margin:0 0 8px 0; color:#a6c3db">Toca una sugerencia:</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("¿Qué es un exoplaneta?"):
                st.session_state._chip_prompt = "¿Qué es un exoplaneta? Explícamelo simple."
            if st.button("¿Puede haber vida allá afuera?"):
                st.session_state._chip_prompt = "¿Crees que puede haber vida en exoplanetas? Explícamelo sencillo."
        with c2:
            if st.button("¿Para qué sirve buscarlos?"):
                st.session_state._chip_prompt = "¿Para qué sirve buscar exoplanetas? Dame 3 razones."
            if st.button("Dato curioso"):
                st.session_state._chip_prompt = "Dame un dato curioso sobre exoplanetas."
        with c3:
            if st.button("¿Qué fue la misión Kepler?"):
                st.session_state._chip_prompt = "¿Qué fue la misión Kepler y por qué fue importante?"
            if st.button("¿Cómo los encontramos?"):
                st.session_state._chip_prompt = "¿Cómo encontramos exoplanetas? Dame una explicación fácil."

    # Render del historial (antes del input)
    for m in st.session_state.chat_msgs[1:]:
        if m["role"] == "user":
            with st.chat_message("user", avatar="🧑‍🚀"):
                st.markdown(m["content"])
        elif m["role"] == "assistant":
            with st.chat_message("assistant", avatar="🐏"):
                st.markdown(_format_asst(m["content"]))

    # Barra de entrada SIEMPRE visible
    chip_prompt = st.session_state.pop("_chip_prompt", None)
    typed_text  = st.chat_input("Escríbele a ExoCimarron…", key="chatbox")
    user_text   = chip_prompt or typed_text

    if user_text:
        # turno del usuario
        st.session_state.chat_msgs.append({"role": "user", "content": user_text})
        with st.chat_message("user", avatar="🧑‍🚀"):
            st.markdown(user_text)

        # turno del asistente (stream)
        with st.chat_message("assistant", avatar="🐏"):
            placeholder = st.empty()
            full = ""
            try:
                for token in stream_ollama(st.session_state.chat_msgs):
                    full += token
                    placeholder.markdown(_format_asst(full) + "▌")
            except Exception:
                full = ("ExoCimarron: ⚠️ No pude conectar con el motor local. "
                        "Verifica que Ollama esté corriendo en 11434 y que el modelo esté cargado.")
                placeholder.markdown(_format_asst(full))
            else:
                placeholder.markdown(_format_asst(full))

        st.session_state.chat_msgs.append({"role": "assistant", "content": full})
        st.stop()   # evita rerender completo





# =========================
# INFO — Método de tránsito (didáctico)
# =========================
def render_info():
    st.title("Aprende — Más")
    tab1, tab2 = st.tabs(["Concepto", "Simulador"])

    with tab1:
        # Sección 1: Concepto básico
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown("""
            Un **exoplaneta** es un planeta que **orbita otra estrella** fuera del Sistema Solar.  
            El método más exitoso para detectarlos es el **método de tránsito**: cuando el planeta pasa
            frente a su estrella, el brillo cae un poquito y de forma **periódica**.

            **Qué medimos:**
            - **Profundidad** (**depth**): qué tan grande es el planeta relativo a la estrella.
            """)
            st.latex(r"\text{depth} \approx \left(\frac{R_p}{R_\star}\right)^2")
            st.markdown("""
            * **Duración:** Se asocia con el **ancho del valle** en la curva de luz. Depende de la velocidad orbital del planeta y del tamaño de la estrella.
            * **Periodo:** La **repetición periódica** del mismo patrón indica el **tiempo que tarda el planeta en dar una vuelta completa** alrededor de su estrella.
            """)
        with c2:
            show_img(IMAGES["kepler"], "Misión Kepler (NASA)")

        st.markdown("---")

        # Sección 2: Método del tránsito (ahora en Concepto)
        st.subheader("Método del tránsito")
        c1, c2 = st.columns(2)
        with c1:
            show_img("https://i.giphy.com/coBd3RjR8tGGh6UOOm.webp", "Animación del tránsito")
        with c2:
            st.markdown("""
            Cuando un exoplaneta pasa frente a su estrella (desde nuestro punto de vista), bloquea una pequeña fracción de su luz. Esto se observa como una disminución periódica en el flujo luminoso registrado en la curva de luz.
            * **(A) Fuera de tránsito:** El planeta no está frente a la estrella. El flujo de luz observado es **constante y normalizado a ~1.0**
            * **(B) Ingreso (ingress):** El planeta comienza a pasar por delante del disco estelar. Se observa una **caída gradual** en el flujo de luz, ya que el planeta empieza a bloquear parte de la superficie estelar.
            * **(C) Mínimo (mid-transit):** El planeta está **alineado con el centro del disco estelar** (si la trayectoria es central). Este punto indica la parte más profunda del "valle" en la curva de luz.
            * **(D) Egreso (egress):** El planeta comienza a salir del disco estelar. La cantidad de luz bloqueada **disminuye gradualmente**, y el flujo **vuelve a su nivel normal (~1.0)** cuando el tránsito termina.
        
            """)
    

    with tab2:
        st.subheader("Juega con un tránsito sintético")
        c = st.columns(6)
        P_days       = c[0].slider("Periodo (días)",            0.5, 500.0, 20.0, 0.5)
        duration_h   = c[1].slider("Duración (horas)",          0.2,  30.0,  5.0, 0.1)
        k_rprs       = c[2].slider("Tamaño relativo rp/rs",     0.005,0.20, 0.05, 0.001, help="Radio planeta / radio estrella")
        b_impact     = c[3].slider("Impacto (b)",               0.0,   1.0,  0.20, 0.01, help="0 centrado, 1 rozando")
        noise_sigma  = c[4].slider("Ruido σ (rel.)",            0.0,   0.01, 0.002, 0.0005)
        vshape       = c[5].slider("Forma U ↔ V",               0.0,   0.60, 0.20, 0.05, help="0 = U suave, 0.6 = V pronunciada")

        star_cols = st.columns(2)
        center_phase= star_cols[0].slider("Centro de tránsito (fase)", 0.1, 0.9, 0.5, 0.01)
        show_marks  = star_cols[1].checkbox("Marcar ingreso/egreso", True)

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
            fig.add_annotation(x=center_phase, y=min(y), text="Centro", showarrow=False, yshift=-10, font=dict(color="#ff66aa"))
        fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10,r=10,t=30,b=10),
                          xaxis_title="Fase orbital (0–1)", yaxis_title="Flux relativo", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        depth_ppm = depth * 1e6
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Profundidad", f"{depth_ppm:,.0f} ppm")
        m2.metric("rp/rs", f"{k_rprs:.3f}")
        m3.metric("Duración", f"{duration_h:.2f} h")
        m4.metric("Duty cycle", f"{duty:.3f}")
        m5, m6 = st.columns(2)
        m5.metric("Radio planeta", f"{k_rprs:.1f} R⊕")
        m6.metric("Impacto (b)", f"{b_impact:.2f}")

# =========================
# GAME — Caza exoplanetas
# =========================
def render_game():
    st.title("🎮 Juega — ¿PLANETA o NO PLANETA?")
    st.caption("Mira la curva de luz y elige. Feedback inmediato.")

    cset = st.columns(5)
    difficulty = cset[0].selectbox("Dificultad", ["Fácil","Media","Difícil"], index=1)
    n_points   = cset[1].number_input("Puntos", 200, 3000, 600, 100)
    rounds     = cset[2].slider("Rondas", 3, 20, 7, 1)
    show_hints = cset[3].checkbox("Ver pistas", True)
    show_truth = cset[4].checkbox("Mostrar solución al fallar", True)
    noise = {"Fácil":0.002, "Media":0.004, "Difícil":0.008}[difficulty]

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
        st.session_state.g_truth = "PLANETA" if is_planet else "NO PLANETA"
        st.session_state.g_xy = (x,y)

    if st.session_state.g_xy is None: new_round()

    x,y = st.session_state.g_xy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(width=2, color="#8bd7ff")))
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10,r=10,t=28,b=10),
                      xaxis_title="Fase orbital (0–1)", yaxis_title="Flux relativo", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    if show_hints:
        st.info("**Pistas:** tránsitos reales suelen ser poco profundos (ppm), simétricos, con forma **U**; falsos a menudo muestran dips **V** agudos o modulación alrededor.")

    b1,b2,b3 = st.columns(3)
    guess = None
    if b1.button("🪐 ¡Es PLANETA!", use_container_width=True): guess="PLANETA"
    if b2.button("🛰️ NO PLANETA", use_container_width=True):  guess="NO PLANETA"
    if b3.button("🔁 Nueva señal", use_container_width=True): new_round()

    if guess is not None:
        truth = st.session_state.g_truth
        if guess == truth:
            st.success("✅ ¡Correcto! +1 punto")
            st.session_state.g_score += 1
        else:
            st.error(f"❌ Incorrecto. Era **{truth}**")
            if show_truth:
                msg = "• Dip suave y simétrico → típico tránsito." if truth=="PLANETA" else "• Dip muy agudo/modulado → no planeta."
                st.caption(f"Explicación: {msg}")
        st.session_state.g_idx += 1
        if st.session_state.g_idx >= rounds:
            st.subheader("🏁 Resultado final")
            st.metric("Puntaje", f"{st.session_state.g_score}/{rounds}")
            if st.button("🧹 Reiniciar"):
                st.session_state.g_idx=0; st.session_state.g_score=0
            new_round()
        else:
            new_round()


# =========================
# PREDICTOR — Leaderboard + selector + multi-predicción
# =========================
def render_predictor():
    st.title(f"🔮 {BRAND}: Predicción — CONFIRMED vs FALSE POSITIVE")

    import os, json, joblib
    import pandas as pd
    import plotly.graph_objects as go

    MODELS_DIR = "models"
    METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")  # precomputado fuera del app

    # -------- Helpers
    def list_models():
        if not os.path.isdir(MODELS_DIR): return []
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

    # -------- Detectar modelos y métricas
    available = list_models()
    if not available:
        st.error("No encontré modelos en `./models`. Sube tus *.pkl a esa carpeta.")
        st.stop()

    metrics = load_metrics()
    feats = load_features()

    # -------- Leaderboard (tabla + barra de accuracy)
    st.subheader("🏆 Leaderboard de modelos")
    rows = []
    for m in available:
        acc = metrics.get(m, {}).get("accuracy", None)
        rows.append({"Modelo": m, "Accuracy": acc})
    leaderboard = pd.DataFrame(rows).sort_values(by="Accuracy", ascending=False, na_position="last")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.dataframe(leaderboard, use_container_width=True)
    with c2:
    # --- BARRAS legibles con márgenes seguros ---
        acc_pct = (leaderboard["Accuracy"].fillna(0) * 100).round(1)

    fig = go.Figure(go.Bar(
        x=leaderboard["Modelo"],
        y=acc_pct,
        text=[f"{v:.1f}%" for v in acc_pct],
        textposition="outside",               # etiquetas fuera
        marker=dict(
            color=["#60A5FA", "#34D399", "#A78BFA", "#F59E0B", "#F472B6", "#7DD3FC"][:len(acc_pct)],
            line=dict(color="rgba(255,255,255,0.35)", width=1.2)
        )
    ))

    # Headroom arriba para que no corte el texto outside
    ymax = float(acc_pct.max() if len(acc_pct) else 100)

    # Márgenes más amplios (especialmente abajo) + automargin en ejes
    fig.update_layout(
        template="plotly_dark",
        height=340,
        margin=dict(l=30, r=50, t=30, b=100),  # <- sube b si aún corta (p.ej. 120)
        yaxis_title="Accuracy (%)",
        xaxis_title=""
    )
    fig.update_xaxes(
        tickangle=-25,
        automargin=True,
        tickfont=dict(size=16, family="Inter, sans-serif")
    )
    fig.update_yaxes(
        range=[0, ymax * 1.15],   # espacio extra arriba para las etiquetas
        tickfont=dict(size=14),
        automargin=True
    )

    # Permite que el texto/barra se renderice fuera del eje sin recortarse
    fig.update_traces(cliponaxis=False)

    st.plotly_chart(fig, use_container_width=True)



    # Top recomendado
    recommended = leaderboard.iloc[0]["Modelo"] if len(leaderboard) else available[0]
    use_rec = st.toggle("Usar recomendado automáticamente", value=True, help="Selecciona el mejor por Accuracy")
    default_index = available.index(recommended) if (use_rec and recommended in available) else 0

    # -------- Selector de modelo (sigue existiendo, pero puede autoseleccionar el mejor)
    sel_col, acc_col = st.columns([1, 1])
    with sel_col:
        model_name = st.selectbox("Modelo activo", available, index=default_index, help="Modelo que usará el gauge y el mensaje")
    with acc_col:
        acc = metrics.get(model_name, {}).get("accuracy", None)
        if acc is not None:
                st.metric("Accuracy (val/test)", f"{acc*100:.2f}%")
        else:
                st.info("Accuracy: N/A (agrega `models/metrics.json`)")

    st.caption("Ajusta valores o usa un preset. Rangos típicos de Kepler.")

    # -------- Presets
    presets = {
        "🌍 Tierra-like": {
            "koi_period": 365.0, "koi_duration": 10.0, "koi_depth": 84.0, "koi_model_snr": 12.0,
            "koi_impact": 0.2, "koi_time0bk": 900.0, "koi_steff": 5750.0, "koi_slogg": 4.45,
            "koi_srad": 1.0, "koi_smet": 0.0, "koi_kepmag": 14.0, "duty_cycle": 10.0/(365*24), "rp_rs": 0.0091
        },
        "🪐 Neptuno": {
            "koi_period": 30.0, "koi_duration": 6.0, "koi_depth": 2000.0, "koi_model_snr": 25.0,
            "koi_impact": 0.3, "koi_time0bk": 700.0, "koi_steff": 5400.0, "koi_slogg": 4.4,
            "koi_srad": 1.0, "koi_smet": -0.1, "koi_kepmag": 13.5, "duty_cycle": 6.0/(30*24), "rp_rs": 0.035
        },
        "🔥 Júpiter caliente": {
            "koi_period": 3.0, "koi_duration": 3.0, "koi_depth": 12000.0, "koi_model_snr": 60.0,
            "koi_impact": 0.1, "koi_time0bk": 500.0, "koi_steff": 6000.0, "koi_slogg": 4.3,
            "koi_srad": 1.2, "koi_smet": 0.2, "koi_kepmag": 12.5, "duty_cycle": 3.0/(3*24), "rp_rs": 0.1
        }
    }
    pc = st.columns(len(presets))
    for (i, (label, values)) in enumerate(presets.items()):
        if pc[i].button(label, use_container_width=True):
            st.session_state.predictor_values.update(values)
            st.toast(f"Preset aplicado: {label}")

    # -------- Sliders (como los tienes)
    slider_spec = [
        ("Periodo orbital (días)",            "koi_period",     0.5,   500.0,  20.0,   0.1,  "Periodo entre tránsitos."),
        ("Duración del tránsito (horas)",     "koi_duration",   0.2,    30.0,   5.0,   0.1,  "Tiempo que dura el tránsito."),
        ("Profundidad del tránsito (ppm)",    "koi_depth",     20.0, 50000.0, 800.0,  10.0,  "Caída de flujo (ppm)."),
        ("SNR del modelo de tránsito",        "koi_model_snr",  1.0,   300.0,  20.0,   0.5,  "Relación señal/ruido."),
        ("Parámetro de impacto (b)",          "koi_impact",     0.0,     1.2,   0.3,   0.01, "0 centrado, 1 rozando."),
        ("Época del tránsito (BKJD)",         "koi_time0bk",  100.0,  2000.0, 900.0,   1.0,  "Barycentric Kepler JD – 2454833."),
        ("Temperatura efectiva estelar (K)",  "koi_steff",   3000.0, 10000.0, 5700.0, 10.0,  "Teff de la estrella."),
        ("Log g estelar (cgs)",               "koi_slogg",      3.0,     5.5,   4.4,   0.01, "Gravedad superficial."),
        ("Radio estelar (R☉)",                "koi_srad",       0.1,    20.0,   1.0,   0.01, "En radios solares."),
        ("Metallicidad [Fe/H] (dex)",         "koi_smet",      -1.0,     0.5,   0.0,   0.01, "Abundancia relativa."),
        ("Magnitud Kepler",                   "koi_kepmag",     9.0,    17.5,  14.0,   0.1,  "Brillo en banda Kepler."),
        ("Duty cycle (duración/periodo)",     "duty_cycle",     0.0,     0.2,   0.01,  0.001,"Fracción del tiempo en tránsito."),
        ("Razón de radios rp/rs",             "rp_rs",          0.005,   0.20,  0.05,  0.001,"~√(depth)."),
    ]
    desired_order = (feats if feats else [s[1] for s in slider_spec])
    spec_by_name = {s[1]: s for s in slider_spec}
    slider_names_ordered = [c for c in desired_order if c in spec_by_name]

    values = {}
    for i in range(0, len(slider_names_ordered), 2):
        c1, c2 = st.columns(2)
        for col, name in zip((c1, c2), slider_names_ordered[i:i+2]):
            label, key, vmin, vmax, vdef, step, help_ = spec_by_name[name]
            default = st.session_state.predictor_values.get(key, vdef)
            with col:
                v = st.slider(label, float(vmin), float(vmax), float(default), float(step), help=help_, key=f"sl_{key}")
                values[key] = v

    sync_depth = st.checkbox("Sincronizar profundidad con rp/rs (depth ≈ (rp/rs)^2)", value=False)
    if sync_depth:
        values["koi_depth"] = float(values.get("rp_rs", 0.0)**2 * 1e6)
        st.session_state["sl_koi_depth"] = values["koi_depth"]

    # -------- Construir X con orden correcto
    X = pd.DataFrame([[values.get(c, 0.0) for c in slider_names_ordered]], columns=slider_names_ordered)
    # Si el modelo guardó feature_names_in_, reordenaremos al vuelo cuando hagamos cada predicción
    # Si no, usamos features.json como orden base
    def align_X_for(model):
        if hasattr(model, "feature_names_in_"):
            Z = X.copy()
            for miss in model.feature_names_in_:
                if miss not in Z.columns: Z[miss] = 0.0
            return Z[model.feature_names_in_]
        elif feats:
            Z = X.copy()
            for miss in feats:
                if miss not in Z.columns: Z[miss] = 0.0
            return Z[feats]
        return X

    st.markdown("---")

    # -------- Botón: predecir con TODOS y mostrar tabla
    if st.button("🚀 Predecir con todos los modelos", use_container_width=True):
        rows_pred = []
        for m in available:
            mdl = load_model(m)
            Xi = align_X_for(mdl)
            yhat = int(mdl.predict(Xi)[0])
            prob = None
            if hasattr(mdl, "predict_proba"):
                p = mdl.predict_proba(Xi)[0]
                prob = float(p[1]) if yhat==1 else float(p[0])
            rows_pred.append({
                "Modelo": m,
                "Predicción": "CONFIRMED" if yhat==1 else "FALSE POSITIVE",
                "Confianza": (None if prob is None else f"{prob*100:.1f}%"),
                "Accuracy(ref)": (None if metrics.get(m, {}).get("accuracy") is None else f"{metrics[m]['accuracy']*100:.2f}%")
            })

        # Ordenar: primero los que predicen CONFIRMED con mayor confianza, luego el resto
        dfp = pd.DataFrame(rows_pred)
        st.subheader("Resultados para este input")
        st.dataframe(dfp, use_container_width=True)

        # Gauge SOLO del modelo seleccionado (para mantener tu UI original)
        mdl_sel = load_model(model_name)
        Xi_sel = align_X_for(mdl_sel)
        yhat_sel = int(mdl_sel.predict(Xi_sel)[0])
        label_sel = "CONFIRMED" if yhat_sel==1 else "FALSE POSITIVE"
        conf_val = None
        if hasattr(mdl_sel, "predict_proba"):
            psel = mdl_sel.predict_proba(Xi_sel)[0]
            conf_val = float(psel[1]) if yhat_sel==1 else float(psel[0])
        (st.success if yhat_sel==1 else st.error)(f"{BRAND} ({model_name}) dice: **{label_sel}** · " + (f"Confianza ≈ {conf_val*100:.1f}%" if conf_val is not None else ""))
        if conf_val is not None:
            gfig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=conf_val*100,
                number={"suffix":"%"},
                gauge={"axis":{"range":[0,100]}, "bar":{"thickness":0.35}},
                domain={"x":[0,1],"y":[0,1]}
            ))
            gfig.update_layout(template="plotly_dark", height=280, margin=dict(l=10,r=10,t=20,b=10))
            st.plotly_chart(gfig, use_container_width=True)

    # Tips
    with st.expander("Consejos rápidos"):
        st.write("""
        - Usa el leaderboard para comparar modelos sin cambiar de vista.
        - El botón **Predecir con todos** te da, para este input, la salida de todos los modelos a la vez.
        - Activa **Usar recomendado** para que el select te elija el mejor automáticamente (por Accuracy).
        """)



# =========================
# ABOUT
# =========================
def render_about():
    st.title("🚀 Acerca del MVP")
    st.markdown(f"""
    <div class="block">
      <p><b>{BRAND}</b> combina ciencia, juego e IA para explicar el método de tránsito de forma accesible.</p>
      <ul>
        <li>Chat didáctico</li>
        <li>Juego de curvas de luz</li>
        <li>Simulador de tránsitos</li>
        <li>Predictor binario (CONFIRMED vs FALSE POSITIVE)</li>
      </ul>
      <p>Reto: <b>A World Away — Hunting for Exoplanets with AI</b> (NASA Space Apps 2025).</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Galería")
    g1,g2,g3 = st.columns(3)
    with g1: show_img(IMAGES["nasa_logo"],   caption="NASA")
    with g2: show_img(IMAGES["kepler"],      caption="Kepler")
    with g3: show_img(IMAGES["transit"],     caption="Tránsito (ESA)")

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
