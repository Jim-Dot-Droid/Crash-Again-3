
import streamlit as st
import pandas as pd
import numpy as np

# ---------- Functions ----------
@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    return df['multiplier'].tolist()

def compute_improved_confidence(data, threshold=2.0, trend_window=10):
    if not data:
        return 0.5, 0.5

    data = np.array(data)
    n = len(data)
    weights = np.linspace(0.3, 1.0, n)
    base_score = np.average((data > threshold).astype(int), weights=weights)
    recent = data[-trend_window:] if n >= trend_window else data
    trend_score = np.mean(recent > threshold) if len(recent) > 0 else 0.5

    streak = 1
    for i in range(n-2, -1, -1):
        if (data[i] > threshold and data[i+1] > threshold) or (data[i] <= threshold and data[i+1] <= threshold):
            streak += 1
        else:
            break
    streak_impact = min(streak * 0.01, 0.1)
    streak_score = streak_impact if data[-1] <= threshold else -streak_impact

    combined = (0.6 * base_score) + (0.3 * trend_score) + (0.1 * (0.5 + streak_score))
    volatility = np.std(data)
    if volatility > 2:
        combined *= 0.9
    if n < 20:
        combined = 0.5 + (combined - 0.5) * 0.7

    combined = max(0, min(combined, 1))
    return combined, 1 - combined

def main():
    st.title("Crash Predictor (Improved v2)")
    st.write("Upload a CSV or enter values manually (you can use percentages like 250%).")
    
    if "data" not in st.session_state:
        st.session_state.data = []

    uploaded_file = st.file_uploader("Upload multipliers CSV", type=["csv"])
    if uploaded_file:
        st.session_state.data = load_csv(uploaded_file)
        st.success(f"Loaded {len(st.session_state.data)} multipliers.")

    st.subheader("Manual Input")
    new_val = st.text_input("Enter a new multiplier (e.g., 1.87 or 250%)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add"):
            try:
                val = float(new_val.strip('%')) / 100 if '%' in new_val else float(new_val)
                st.session_state.data.append(val)
                st.success(f"Added {val:.2f}")
            except:
                st.error("Invalid number.")
    with col2:
        if st.button("Clear History"):
            st.session_state.data = []
            st.success("History cleared.")

    if st.session_state.data:
        above_conf, under_conf = compute_improved_confidence(st.session_state.data)
        st.subheader("Prediction")
        if above_conf > under_conf:
            st.write(f"Prediction: **Above 200%** ({above_conf:.1%} confidence)")
        else:
            st.write(f"Prediction: **Under 200%** ({under_conf:.1%} confidence)")
        st.write(f"Entries so far: **{len(st.session_state.data)}**")
    else:
        st.write("Add data to get prediction.")

if __name__ == "__main__":
    main()
