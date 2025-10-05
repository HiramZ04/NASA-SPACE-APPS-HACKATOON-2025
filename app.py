# app.py
import json, joblib, numpy as np, pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="KOI Classifier", page_icon="🪐", layout="wide")
st.title("🪐 Kepler: Confirmed vs False Positive")

HERE = Path(__file__).parent
MODEL_PATH = HERE / "model.pkl"
FEATS_PATH = HERE / "features.json"

# Carga robusta con mensaje si falta algo
try:
    with st.spinner("Cargando modelo..."):
        model = joblib.load(MODEL_PATH)
        FEATURES = json.load(open(FEATS_PATH))
except Exception as e:
    st.error(f"No pude cargar artefactos.\n\n**Esperaba**:\n- `{MODEL_PATH.name}`\n- `{FEATS_PATH.name}`\n\n**Error**: {e}")
    st.info("Pon `model.pkl` y `features.json` en la misma carpeta que `app.py` y vuelve a ejecutar: `streamlit run app.py`")
    st.stop()

st.sidebar.header("Opciones")
threshold = st.sidebar.slider("Umbral P(CONFIRMED)", 0.05, 0.95, 0.50, 0.01)
mode = st.sidebar.radio("Modo", ["Formulario", "CSV"])

if mode == "Formulario":
    cols = st.columns(3)
    vals = []
    for i, col in enumerate(FEATURES):
        with cols[i % 3]:
            vals.append(st.number_input(col, value=0.0, step=0.001, format="%.6f"))

    if st.button("Predecir", type="primary"):
        x = np.array([vals], dtype=float)
        # Si tu modelo NO es pipeline con imputer y hay NaN, quítalos o rellena aquí:
        if np.isnan(x).any():
            st.warning("Había NaN en la entrada; los rellené con 0.0 para poder predecir.")
            x = np.nan_to_num(x, nan=0.0)
        proba = float(model.predict_proba(x)[0, 1])   # asumiendo 1=CONFIRMED
        pred = "CONFIRMED" if proba >= threshold else "FALSE POSITIVE"
        st.success(f"{pred} — P(CONFIRMED)={proba:.3f} (umbral {threshold:.2f})")

else:
    st.caption("Sube un CSV con **exactamente** estas columnas (cualquier orden):")
    st.code(", ".join(FEATURES))
    up = st.file_uploader("CSV", type=["csv"])
    if up is not None:
        df = pd.read_csv(up)
        missing = [c for c in FEATURES if c not in df.columns]
        if missing:
            st.error(f"Faltan columnas: {missing}")
        else:
            X = df.reindex(columns=FEATURES).apply(pd.to_numeric, errors="coerce")
            if X.isna().any().any():
                st.info("Se detectaron NaN; los relleno con 0.0 para predecir.")
                X = X.fillna(0.0)
            probs = model.predict_proba(X.values)[:, 1]
            labels = np.where(probs >= threshold, "CONFIRMED", "FALSE POSITIVE")
            out = df.copy()
            out["P_confirmed"] = probs
            out["pred"] = labels
            st.dataframe(out.head(20), use_container_width=True)
            st.download_button("⬇️ Descargar predicciones", out.to_csv(index=False).encode(), "predicciones_koi.csv", "text/csv")
