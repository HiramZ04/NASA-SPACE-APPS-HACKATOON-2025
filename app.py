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

# Create tabs
tab1, tab2, tab3 = st.tabs(["🤖 Model", "💬 Chatbot", "ℹ️ Information"])

with tab1:
    st.header("Model Prediction")
    
    # Model options in main page
    mode = st.radio("Prediction Mode", ["Form", "CSV Upload"], horizontal=True)
    
    st.markdown("---")

    if mode == "Form":
        st.subheader("📝 Manual Input Form")
        
        # Predict button at the top
        predict_button = st.button("🔮 Predict", type="primary", use_container_width=True)
        
        # Results section at the top (initially empty)
        results_container = st.container()
        
        # Display required features in an expandable section
        with st.expander("ℹ️ Required Features", expanded=False):
            st.write("The model requires the following features:")
            feature_df = pd.DataFrame({"Feature Name": FEATURES})
            st.dataframe(feature_df, use_container_width=True, hide_index=True)
        
        # Create form for manual input
        st.write("**Enter values for each feature:**")
        
        cols = st.columns(3)
        vals = []
        
        for i, feature in enumerate(FEATURES):
            with cols[i % 3]:
                # Slider limits
                min_val, max_val = -10.0, 10.0
                
                # Create a container for synchronized inputs
                container = st.container()
                
                with container:
                    # Number input (primary control)
                    number_val = st.number_input(
                        f"**{feature}**", 
                        value=0.0, 
                        step=0.001, 
                        format="%.6f",
                        key=f"number_{i}"
                    )
                    
                    # Slider (synchronized with number input, clamped to range)
                    slider_display_val = max(min_val, min(max_val, number_val))
                    slider_val = st.slider(
                        f"Range: {min_val} to {max_val}", 
                        min_value=min_val, 
                        max_value=max_val, 
                        value=slider_display_val, 
                        step=0.01,
                        key=f"slider_{i}",
                        label_visibility="visible"
                    )
                    
                    # If slider was moved, update the number input value
                    if abs(slider_val - slider_display_val) > 0.001:
                        # Slider was changed, use slider value
                        vals.append(slider_val)
                        # Update number input to match slider (this will happen on next run)
                        if f"number_{i}" in st.session_state:
                            st.session_state[f"number_{i}"] = slider_val
                    else:
                        # Use number input value
                        vals.append(number_val)
                    
                    # Show warning if number input exceeds slider range
                    if number_val < min_val or number_val > max_val:
                        if number_val < min_val:
                            st.caption(f"⚠️ Value below slider minimum ({min_val})")
                        else:
                            st.caption(f"⚠️ Value above slider maximum ({max_val})")
        
        # Results section for form
        if predict_button:
            with results_container:
                st.subheader("🎯 Prediction Results")
                
                x = np.array([vals], dtype=float)
                
                # Handle NaN values
                if np.isnan(x).any():
                    st.warning("⚠️ Some values were NaN; replaced with 0.0 for prediction.")
                    x = np.nan_to_num(x, nan=0.0)
                
                # Make prediction (using fixed threshold of 0.5)
                proba = float(model.predict_proba(x)[0, 1])
                pred = "CONFIRMED" if proba >= 0.5 else "FALSE POSITIVE"
                
                # Display results prominently
                col1, col2 = st.columns(2)
                
                with col1:
                    if pred == "CONFIRMED":
                        st.success(f"✅ **{pred}**")
                    else:
                        st.error(f"❌ **{pred}**")
                
                with col2:
                    st.metric("Probability", f"{proba:.3f}")
                
                # Additional visualization
                st.progress(proba, text=f"Confidence: {proba:.1%}")

    else:  # CSV Upload mode
        st.subheader("📁 CSV Upload")
        
        # Show required columns in collapsible table format
        with st.expander("📋 Required Columns", expanded=False):
            st.write("**Your CSV file must contain these exact column names:**")
            
            # Create a nice table showing required features
            feature_table = pd.DataFrame({
                "Column Name": FEATURES,
                "Required": ["✅"] * len(FEATURES),
                "Type": ["Numeric"] * len(FEATURES)
            })
            
            st.dataframe(feature_table, use_container_width=True, hide_index=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose your CSV file", 
            type=["csv"],
            help="Upload a CSV file with the required column names"
        )
        
        # Process uploaded file
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Check for missing columns
                missing = [c for c in FEATURES if c not in df.columns]
                extra = [c for c in df.columns if c not in FEATURES]
                
                if missing:
                    st.error(f"❌ **Missing required columns:** {', '.join(missing)}")
                else:
                    st.success("✅ **All required columns found!**")
                    
                    if extra:
                        st.info(f"ℹ️ **Extra columns found (will be included in output):** {', '.join(extra)}")
                    
                    # Process data
                    X = df.reindex(columns=FEATURES).apply(pd.to_numeric, errors="coerce")
                    
                    if X.isna().any().any():
                        st.warning("⚠️ Some NaN values detected; replaced with 0.0 for prediction.")
                        X = X.fillna(0.0)
                    
                    # Make predictions (using fixed threshold of 0.5)
                    probs = model.predict_proba(X.values)[:, 1]
                    labels = np.where(probs >= 0.5, "CONFIRMED", "FALSE POSITIVE")
                    
                    # Create output dataframe
                    out = df.copy()
                    out["P_confirmed"] = probs
                    out["Prediction"] = labels
                    
                    # Results section for CSV
                    st.markdown("---")
                    st.subheader("🎯 Prediction Results")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Records", len(out))
                    
                    with col2:
                        confirmed_count = (labels == "CONFIRMED").sum()
                        st.metric("Confirmed", confirmed_count)
                    
                    with col3:
                        false_positive_count = (labels == "FALSE POSITIVE").sum()
                        st.metric("False Positive", false_positive_count)
                    
                    with col4:
                        avg_confidence = probs.mean()
                        st.metric("Avg Confidence", f"{avg_confidence:.3f}")
                    
                    # Show data preview
                    st.write("**Results Preview (first 20 rows):**")
                    st.dataframe(out.head(20), use_container_width=True)
                    
                    # Download button
                    csv_data = out.to_csv(index=False).encode()
                    st.download_button(
                        "⬇️ Download Full Results", 
                        csv_data, 
                        "koi_predictions.csv", 
                        "text/csv",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"❌ **Error processing file:** {str(e)}")

with tab2:
    st.header("Chatbot")
    st.info("🚧 Chatbot functionality coming soon!")

with tab3:
    st.header("Information")
    st.info("ℹ️ Information section coming soon!")
