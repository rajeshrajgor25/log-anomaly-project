"""
Log Anomaly Detection Frontend
Streamlit web application
"""
import streamlit as st
import requests
import pandas as pd
import os
from typing import List, Dict, Any

# Configuration
API_BASE_URL = os.environ.get("API_URL", "http://backend:8000")


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def predict_anomalies(logs: List[str]) -> List[Dict[str, Any]]:
    """Call API to predict anomalies"""
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json={"logs": logs}
    )
    response.raise_for_status()
    return response.json()


def train_model(logs: List[str]) -> Dict[str, Any]:
    """Call API to train model"""
    response = requests.post(
        f"{API_BASE_URL}/train",
        json={"logs": logs}
    )
    response.raise_for_status()
    return response.json()


def main():
    st.set_page_config(
        page_title="Log Anomaly Detector",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Log Anomaly Detection")
    st.markdown("Detect anomalies in your log files using machine learning")
    
    # Sidebar
    st.sidebar.header("Settings")
    api_url = st.sidebar.text_input(
        "API URL",
        value=API_BASE_URL,
        help="Backend API endpoint"
    )
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Cannot connect to API. Make sure the backend is running.")
        st.info(f"Expected API at: {api_url}")
        return
    
    st.success("✅ Connected to API")
    
    # Main content
    tab1, tab2 = st.tabs(["🔍 Detect Anomalies", "📊 Results"])
    
    with tab1:
        st.subheader("Enter Log Entries")

        # Input method selection
        input_method = st.radio(
            "Input method:",
            ["Text area", "File upload"],
            horizontal=True
        )

        logs = []
        detect_triggered = False

        if input_method == "Text area":
            log_input = st.text_area(
                "Enter logs (one per line):",
                height=200,
                placeholder="INFO: Application started\nERROR: Database timeout\nINFO: User logged in",
                key="log_input",
                on_change=lambda: st.session_state.update({"detect_ready": True})
            )
            if log_input:
                logs = [line.strip() for line in log_input.split("\n") if line.strip()]
            # Detect on Enter (Ctrl+Enter)
            if st.session_state.get("detect_ready") and len(logs) > 0:
                detect_triggered = True
                st.session_state["detect_ready"] = False

        else:
            uploaded_file = st.file_uploader(
                "Upload log file",
                type=["log", "txt"]
            )
            if uploaded_file:
                content = uploaded_file.getvalue().decode("utf-8")
                logs = [line.strip() for line in content.split("\n") if line.strip()]

        # Predict button
        detect_btn = st.button("Detect Anomalies", type="primary", disabled=len(logs) == 0)
        if detect_btn or detect_triggered:
            with st.spinner("Analyzing logs..."):
                try:
                    results = predict_anomalies(logs)
                    st.session_state["results"] = results
                    st.session_state["logs"] = logs
                    st.session_state["active_tab"] = 1  # Switch to Results tab
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Switch to Results tab if detection just happened
    active_tab = st.session_state.get("active_tab", 0)
    with tab2:
        if "results" not in st.session_state:
            st.info("No results yet. Go to 'Detect Anomalies' tab to analyze logs.")
            return
        
        results = st.session_state["results"]
        
        # Summary statistics
        anomalies = [r for r in results if r["is_anomaly"]]
        normal = [r for r in results if not r["is_anomaly"]]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Logs", len(results))
        col2.metric("Anomalies", len(anomalies), delta_color="inverse")
        col3.metric("Normal", len(normal))
        
        # Results table
        st.subheader("Analysis Results")
        
        df = pd.DataFrame(results)
        df["anomaly_score"] = df["anomaly_score"].round(4)
        
        # Use text labels for status
        def status_label(val):
            return "Anomaly" if val else "Normal"

        df["Status"] = df["is_anomaly"].apply(status_label)
        
        # Display with filtering
        filter_option = st.selectbox(
            "Filter:",
            ["All", "Anomalies only", "Normal only"]
        )
        
        if filter_option == "Anomalies only":
            df = df[df["is_anomaly"] == True]
        elif filter_option == "Normal only":
            df = df[df["is_anomaly"] == False]
        
        st.dataframe(
            df[["Status", "log", "anomaly_score"]],
            use_container_width=True,
            height=400
        )
        
        # Download results
        if len(df) > 0:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Results",
                data=csv,
                file_name="anomaly_results.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()