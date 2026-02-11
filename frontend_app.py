"""
Streamlit Frontend for Credit Card Fraud Detection System
Beautiful, interactive UI for real-time fraud detection
"""
import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Fraud Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .decision-allow {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0;
    }
    .decision-review {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0;
    }
    .decision-block {
        padding: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"

# App Header
st.markdown('<div class="main-header">🛡️ Credit Card Fraud Detection</div>', unsafe_allow_html=True)
st.markdown("### Real-time transaction fraud analysis using Machine Learning")

# Sidebar for examples and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.write("**Backend API:**")
    st.code(API_URL, language="bash")
    
    # Health check
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            st.success("✅ API Connected")
            if data.get("model_loaded"):
                st.info("🤖 Model Ready")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Not Running")
        st.warning("Start backend: `python backend_api.py`")
    
    st.markdown("---")
    st.header("📋 Quick Examples")
    
    example_type = st.selectbox(
        "Load Example",
        ["Custom", "Normal Transaction", "Suspicious Transaction", "High-Risk Transaction"]
    )

# Example transaction templates
examples = {
    "Normal Transaction": {
        "amt": 89.50,
        "city_pop": 150000,
        "lat": 40.7128,
        "long": -74.0060,
        "merch_lat": 40.7500,
        "merch_long": -73.9900,
        "distance_km": 5.2,
        "txn_time_gap": 3600.0,
        "txn_count_1h": 1,
        "avg_amt_per_card": 95.0,
        "amt_deviation": 0.94,
        "customer_age": 35,
        "txn_hour": 14,
        "is_weekend": 0,
        "gender": "F",
        "state": "NY",
        "category": "grocery_pos",
        "merchant": "Whole Foods",
        "cc_num": "card_12345"
    },
    "Suspicious Transaction": {
        "amt": 2500.00,
        "city_pop": 50000,
        "lat": 40.7128,
        "long": -74.0060,
        "merch_lat": 34.0522,
        "merch_long": -118.2437,
        "distance_km": 3944.0,
        "txn_time_gap": 120.0,
        "txn_count_1h": 8,
        "avg_amt_per_card": 100.0,
        "amt_deviation": 25.0,
        "customer_age": 28,
        "txn_hour": 2,
        "is_weekend": 1,
        "gender": "M",
        "state": "CA",
        "category": "misc_net",
        "merchant": "Unknown_Merchant",
        "cc_num": "card_67890"
    },
    "High-Risk Transaction": {
        "amt": 4999.99,
        "city_pop": 25000,
        "lat": 40.7128,
        "long": -74.0060,
        "merch_lat": 47.6062,
        "merch_long": -122.3321,
        "distance_km": 3876.0,
        "txn_time_gap": 30.0,
        "txn_count_1h": 15,
        "avg_amt_per_card": 75.0,
        "amt_deviation": 66.67,
        "customer_age": 22,
        "txn_hour": 3,
        "is_weekend": 1,
        "gender": "M",
        "state": "WA",
        "category": "shopping_net",
        "merchant": "Suspicious_Shop_XYZ",
        "cc_num": "card_99999"
    }
}

# Load example if selected
default_values = examples.get(example_type, {})

# Main form
st.markdown("## 💳 Transaction Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💰 Transaction Info")
    amt = st.number_input(
        "Amount ($)",
        min_value=0.01,
        value=float(default_values.get("amt", 100.0)),
        step=0.01,
        help="Transaction amount in USD"
    )
    
    category = st.selectbox(
        "Category",
        ["grocery_pos", "gas_transport", "misc_net", "shopping_net", "shopping_pos", 
         "food_dining", "personal_care", "health_fitness", "travel", "entertainment"],
        index=0 if not default_values else ["grocery_pos", "gas_transport", "misc_net", "shopping_net", "shopping_pos", 
         "food_dining", "personal_care", "health_fitness", "travel", "entertainment"].index(default_values.get("category", "grocery_pos"))
    )
    
    merchant = st.text_input(
        "Merchant",
        value=default_values.get("merchant", "Sample_Merchant"),
        help="Merchant name"
    )
    
    txn_hour = st.slider(
        "Transaction Hour",
        0, 23,
        value=int(default_values.get("txn_hour", 14)),
        help="Hour of the day (0-23)"
    )
    
    is_weekend = st.selectbox(
        "Weekend?",
        [0, 1],
        format_func=lambda x: "Yes" if x == 1 else "No",
        index=int(default_values.get("is_weekend", 0))
    )

with col2:
    st.subheader("👤 Customer Info")
    customer_age = st.slider(
        "Customer Age",
        18, 100,
        value=int(default_values.get("customer_age", 35)),
        help="Customer age in years"
    )
    
    gender = st.selectbox(
        "Gender",
        ["M", "F"],
        index=0 if default_values.get("gender", "M") == "M" else 1
    )
    
    state = st.text_input(
        "State Code",
        value=default_values.get("state", "NY"),
        max_chars=2,
        help="2-letter US state code"
    ).upper()
    
    city_pop = st.number_input(
        "City Population",
        min_value=0,
        value=int(default_values.get("city_pop", 50000)),
        step=1000,
        help="Population of the city"
    )
    
    cc_num = st.text_input(
        "Card Number (Tokenized)",
        value=default_values.get("cc_num", "card_12345"),
        help="Hashed or tokenized card number"
    )

with col3:
    st.subheader("📍 Location & Behavior")
    lat = st.number_input(
        "Customer Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=float(default_values.get("lat", 40.7128)),
        format="%.4f"
    )
    
    long = st.number_input(
        "Customer Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=float(default_values.get("long", -74.0060)),
        format="%.4f"
    )
    
    merch_lat = st.number_input(
        "Merchant Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=float(default_values.get("merch_lat", 40.7500)),
        format="%.4f"
    )
    
    merch_long = st.number_input(
        "Merchant Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=float(default_values.get("merch_long", -73.9900)),
        format="%.4f"
    )
    
    distance_km = st.number_input(
        "Distance to Merchant (km)",
        min_value=0.0,
        value=float(default_values.get("distance_km", 5.0)),
        step=0.1,
        help="Distance from customer to merchant"
    )

# Advanced features (collapsible)
with st.expander("🔧 Advanced Features"):
    col_a, col_b = st.columns(2)
    
    with col_a:
        txn_time_gap = st.number_input(
            "Time Since Last Transaction (seconds)",
            min_value=0.0,
            value=float(default_values.get("txn_time_gap", 3600.0)),
            step=60.0
        )
        
        txn_count_1h = st.number_input(
            "Transactions in Last Hour",
            min_value=0,
            value=int(default_values.get("txn_count_1h", 1)),
            step=1
        )
    
    with col_b:
        avg_amt_per_card = st.number_input(
            "Average Amount per Card",
            min_value=0.0,
            value=float(default_values.get("avg_amt_per_card", 100.0)),
            step=10.0
        )
        
        amt_deviation = st.number_input(
            "Amount Deviation",
            min_value=0.0,
            value=float(default_values.get("amt_deviation", 1.0)),
            step=0.1,
            help="Deviation from average spending"
        )

# Predict button
st.markdown("---")
if st.button("🔍 Analyze Transaction", type="primary"):
    # Prepare request payload
    payload = {
        "amt": amt,
        "city_pop": city_pop,
        "lat": lat,
        "long": long,
        "merch_lat": merch_lat,
        "merch_long": merch_long,
        "distance_km": distance_km,
        "txn_time_gap": txn_time_gap,
        "txn_count_1h": txn_count_1h,
        "avg_amt_per_card": avg_amt_per_card,
        "amt_deviation": amt_deviation,
        "customer_age": customer_age,
        "txn_hour": txn_hour,
        "is_weekend": is_weekend,
        "gender": gender,
        "state": state,
        "category": category,
        "merchant": merchant,
        "cc_num": cc_num
    }
    
    try:
        with st.spinner("🤖 Analyzing transaction..."):
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display decision with appropriate styling
                decision = result["decision"]
                if decision == "ALLOW":
                    st.markdown(
                        f'<div class="decision-allow">✅ {result["message"]}</div>',
                        unsafe_allow_html=True
                    )
                elif decision == "REVIEW":
                    st.markdown(
                        f'<div class="decision-review">⚠️ {result["message"]}</div>',
                        unsafe_allow_html=True
                    )
                else:  # BLOCK
                    st.markdown(
                        f'<div class="decision-block">🚫 {result["message"]}</div>',
                        unsafe_allow_html=True
                    )
                
                # Display metrics
                st.markdown("### 📊 Detailed Analysis")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric(
                        "Fraud Probability",
                        f"{result['fraud_probability']:.2%}",
                        delta=None
                    )
                
                with metric_col2:
                    st.metric(
                        "Prediction",
                        "FRAUD" if result['fraud_prediction'] == 1 else "LEGITIMATE",
                        delta=None
                    )
                
                with metric_col3:
                    st.metric(
                        "Decision",
                        result['decision'],
                        delta=None
                    )
                
                with metric_col4:
                    st.metric(
                        "Confidence",
                        result['confidence'].upper(),
                        delta=None
                    )
                
                # Show risk indicators
                st.markdown("### 🎯 Risk Indicators")
                
                prob = result['fraud_probability']
                st.progress(prob)
                
                if prob >= 0.8:
                    st.error(f"**Very High Risk** ({prob:.1%}) - Immediate action required")
                elif prob >= 0.5:
                    st.warning(f"**Moderate Risk** ({prob:.1%}) - Manual review recommended")
                elif prob >= 0.2:
                    st.info(f"**Low Risk** ({prob:.1%}) - Transaction appears normal")
                else:
                    st.success(f"**Very Low Risk** ({prob:.1%}) - Safe transaction")
                
                # Show raw response
                with st.expander("🔍 View Raw API Response"):
                    st.json(result)
            
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.code(response.text)
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running:")
        st.code("python backend_api.py", language="bash")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>🛡️ Credit Card Fraud Detection System v2.0</p>
    <p>Powered by XGBoost ML • FastAPI Backend • Streamlit Frontend</p>
</div>
""", unsafe_allow_html=True)
