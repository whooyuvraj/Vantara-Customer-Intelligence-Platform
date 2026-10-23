import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Customer Behavior & Churn Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Behavior & Churn Prediction Dashboard")
st.markdown("Predict customer churn risk and analyze RFM segments in real-time.")

# Sidebar for customer metric input
st.sidebar.header("Customer Profile Inputs")

recency = st.sidebar.number_input("Recency (Days since last purchase)", min_value=0.0, value=45.0)
frequency = st.sidebar.number_input("Frequency (Total orders count)", min_value=1.0, value=4.0)
monetary = st.sidebar.number_input("Monetary Value ($ Total spend)", min_value=0.0, value=650.0)
avg_basket = st.sidebar.number_input("Avg Basket Size (Items per order)", min_value=1.0, value=6.0)
total_orders = st.sidebar.number_input("Total Orders", min_value=1.0, value=4.0)
return_count = st.sidebar.number_input("Return Count", min_value=0.0, value=0.0)
return_rate = st.sidebar.number_input("Return Rate", min_value=0.0, max_value=1.0, value=0.0)
avg_order_val = st.sidebar.number_input("Avg Order Value ($)", min_value=0.0, value=162.5)

API_URL = "http://127.0.0.1:8000/predict"

if st.sidebar.button("Run Churn Prediction"):
    payload = {
        "Recency": recency,
        "Frequency": frequency,
        "Monetary": monetary,
        "AvgBasketSize": avg_basket,
        "TotalOrders": total_orders,
        "ReturnCount": return_count,
        "ReturnRate": return_rate,
        "AvgOrderValue": avg_order_val
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()

            col1, col2, col3 = st.columns(3)
            col1.metric("Churn Risk Level", result["risk_level"])
            col2.metric("Churn Probability", f"{result['churn_probability'] * 100:.1f}%")
            col3.metric("Assigned RFM Cluster", f"Cluster {result['assigned_cluster']}")

            if result["churn_prediction"] == 1:
                st.error("⚠️ HIGH CHURN RISK: Customer is likely to stop purchasing in the next 90 days.")
            else:
                st.success("✅ LOW CHURN RISK: Customer is active and engaged.")
        else:
            st.error(f"API Error: Received status code {response.status_code}")
    except Exception as e:
        st.error(f"Failed to connect to FastAPI service. Ensure `uvicorn app:app` is running on port 8000.\nError: {e}")

# Historical Segmentation Overview
st.divider()
st.subheader("Customer Segment Overview")

try:
    df_features = pd.read_csv("data/processed/customer_features.csv")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig_segment = px.pie(
            df_features,
            names='Segment_Name',
            title='Customer Base Breakdown by Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_segment, use_container_width=True)

    with col_chart2:
        fig_scatter = px.scatter(
            df_features,
            x='Recency',
            y='Monetary',
            color='Segment_Name',
            title='Recency vs. Monetary Spend by Segment',
            log_y=True,
            hover_data=['Frequency']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

except Exception as e:
    st.info("Processed data table not found for charts.")
