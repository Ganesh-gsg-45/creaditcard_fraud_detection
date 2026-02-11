# 🛡️ Credit Card Fraud Detection System

A **production-ready** fraud detection application with FastAPI backend and Streamlit frontend, featuring real-time ML-powered fraud analysis with 3-tier decision logic.

---

## 🌟 Features

- ⚡ **FastAPI Backend** - High-performance REST API with automatic documentation
- 🎨 **Streamlit Frontend** - Beautiful, interactive web interface
- 🤖 **XGBoost ML Model** - Trained on real credit card transaction data
- 🎯 **3-Tier Decision Logic** - BLOCK / REVIEW / ALLOW based on risk thresholds
- ✅ **Pydantic Validation** - Automatic request validation
- 📊 **Real-Time Analysis** - Instant fraud probability calculation
- 🔒 **Production Ready** - CORS, error handling, logging included

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Train the Model (if not already done)
```bash
python src/components/data_ingestion.py
python src/components/data_transformation.py
python src/components/model_training.py
```

### 3. Run the Application

#### Terminal 1: Start Backend
```bash
python backend_api.py
```
**Backend runs on:** http://localhost:8000

#### Terminal 2: Start Frontend
```bash
streamlit run frontend_app.py
```
**Frontend opens at:** http://localhost:8501

---

## 🎯 How to Use

1. **Open** http://localhost:8501 in your browser
2. **Select** an example transaction from sidebar OR enter custom data
3. **Fill in** transaction details:
   - 💰 Transaction info (amount, category, merchant)
   - 👤 Customer info (age, gender, location)
   - 📍 Location & behavior (distance, time patterns)
4. **Click** "Analyze Transaction"
5. **View** results with color-coded decision

### Decision Logic

| Fraud Probability | Decision | Action |
|------------------|----------|---------|
| **≥ 0.8** | 🚫 **BLOCK** | Transaction rejected |
| **0.5 - 0.8** | ⚠️ **REVIEW** | Manual review required |
| **< 0.5** | ✅ **ALLOW** | Transaction approved |

---

## 📁 Project Structure

```
creadit-card-fraud/
├── backend_api.py              # FastAPI backend ⭐ NEW
├── frontend_app.py             # Streamlit frontend ⭐ NEW
├── requirements.txt            # All dependencies
├── setup.py                    # Package setup
├── README.md                   # This file
├── artifacts/                  # Model artifacts
│   ├── xgb_model.pkl          # Trained XGBoost model
│   ├── preprocessor.pkl       # Data preprocessor
│   └── model_metrics.json     # Evaluation metrics
├── src/
│   ├── config.py              # Configuration
│   ├── logger.py              # Logging utilities
│   ├── exception.py           # Exception handling
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_training.py
│   └── pipeline/
│       └── predict_pipeline.py
├── tests/                      # Unit tests
├── examples/                   # Usage examples
└── legacy_backup/              # Old Flask app (archived)
```

---

## 🔧 API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check + model status |
| `/predict` | POST | Fraud prediction |
| `/docs` | GET | Interactive API docs (Swagger UI) |

### Example API Call

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amt": 120.50,
    "city_pop": 50000,
    "lat": 40.7128,
    "long": -74.0060,
    "merch_lat": 40.7500,
    "merch_long": -73.9900,
    "distance_km": 5.2,
    "txn_time_gap": 3600.0,
    "txn_count_1h": 2,
    "avg_amt_per_card": 100.0,
    "amt_deviation": 1.2,
    "customer_age": 35,
    "txn_hour": 14,
    "is_weekend": 0,
    "gender": "M",
    "state": "NY",
    "category": "grocery_pos",
    "merchant": "Whole Foods",
    "cc_num": "card_12345"
  }'
```

**Response:**
```json
{
  "fraud_probability": 0.1234,
  "fraud_prediction": 0,
  "decision": "ALLOW",
  "confidence": "high",
  "message": "✅ Transaction ALLOWED - Low fraud risk"
}
```

---

## 📊 Model Performance

Check `artifacts/model_metrics.json` for detailed metrics:
- **ROC-AUC Score**: Overall model performance
- **Precision**: Accuracy of fraud predictions
- **Recall**: Percentage of fraud caught
- **F1-Score**: Harmonic mean of precision & recall
- **Confusion Matrix**: Detailed breakdown

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Test Individual Components
```bash
# Test prediction pipeline
python examples/predict_example.py

# Test data transformation
python src/components/data_transformation.py

# Test model training
python src/components/model_training.py
```

---

## 🎨 Example Transactions

The app includes pre-loaded examples:

1. **Normal Transaction** - Grocery purchase at 2 PM
   - Expected: ALLOW (probability < 0.2)

2. **Suspicious Transaction** - Cross-country late-night purchase
   - Expected: REVIEW (probability 0.5-0.8)

3. **High-Risk Transaction** - $5K at 3 AM with many recent transactions
   - Expected: BLOCK (probability ≥ 0.8)

---

## 🔒 Security & Privacy

> **⚠️ Important for Production:**
> - Hash or tokenize credit card numbers
> - Implement proper authentication
> - Use HTTPS in production
> - Set specific CORS origins
> - Add rate limiting
> - Follow PCI DSS compliance

---

## 📈 Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **ML Model**: XGBoost
- **Validation**: Pydantic
- **Testing**: Pytest
- **Data**: Pandas, NumPy, Scikit-learn

---

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure port 8000 is available
- Check that model files exist in `artifacts/`
- Run: `python backend_api.py` directly to see errors

**Frontend can't connect:**
- Make sure backend is running first
- Check backend URL in `frontend_app.py` (default: localhost:8000)
- Verify firewall settings

**Model not found:**
- Train the model using the pipeline scripts
- Check `artifacts/` directory exists

---

## 👤 Author

**Ganesh**  
Email: tarigondaganesh1234@gmail.com

---

## 📝 Changelog

### v2.0 (Current) - FastAPI + Streamlit
- ✅ Modern FastAPI backend with auto-docs
- ✅ Interactive Streamlit frontend
- ✅ 3-tier decision logic (BLOCK/REVIEW/ALLOW)
- ✅ Pydantic validation
- ✅ Pre-loaded example transactions

### v1.0 (Legacy) - Flask
- Simple Flask API (moved to `legacy_backup/`)

---

## 📄 License

This project is for educational and demonstration purposes.

---

**🎉 Start detecting fraud in real-time with beautiful UI!**

```bash
# Terminal 1
python backend_api.py

# Terminal 2  
streamlit run frontend_app.py

# Open: http://localhost:8501
```
