# 🛡️ Full-Stack Fraud Detection Web Application

A modern, production-ready fraud detection system with FastAPI backend and Streamlit frontend.

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│  Streamlit UI   │────────▶│   FastAPI API    │────────▶│  XGBoost    │
│  (Port 8501)    │  HTTP   │   (Port 8000)    │         │   Model     │
└─────────────────┘         └──────────────────┘         └─────────────┘
```

## ✨ Features

### Backend (FastAPI)
- ✅ REST API with automatic OpenAPI documentation
- ✅ Pydantic models for request validation
- ✅ 3-tier decision logic: **ALLOW** / **REVIEW** / **BLOCK**
- ✅ CORS enabled for frontend integration
- ✅ Health check endpoint
- ✅ Comprehensive error handling

### Frontend (Streamlit)
- ✅ Beautiful, intuitive web interface
- ✅ Interactive form with smart widgets
- ✅ Pre-loaded example transactions
- ✅ Real-time fraud analysis
- ✅ Color-coded decision display
- ✅ Detailed risk indicators
- ✅ API health monitoring

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Model is Trained

Make sure you have trained artifacts:
- `artifacts/xgb_model.pkl`
- `artifacts/preprocessor.pkl`

If not, train the model:
```bash
python src/components/data_ingestion.py
python src/components/data_transformation.py
python src/components/model_training.py
```

### 3. Start the Backend (Terminal 1)

```bash
python backend_api.py
```

**Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Model loaded from artifacts/xgb_model.pkl
✅ Preprocessor loaded from artifacts/preprocessor.pkl
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**API Documentation:** http://localhost:8000/docs

### 4. Start the Frontend (Terminal 2)

```bash
streamlit run frontend_app.py
```

**Output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Open in browser:** http://localhost:8501

---

## 📋 How to Use

### Using the Web Interface

1. **Open:** http://localhost:8501
2. **Choose an example** from the sidebar or enter custom transaction data
3. **Fill in transaction details:**
   - Transaction Info: amount, category, merchant, time
   - Customer Info: age, gender, state, city
   - Location: customer and merchant coordinates
4. **Click "Analyze Transaction"**
5. **View results:**
   - Decision: ALLOW / REVIEW / BLOCK
   - Fraud probability with visual indicator
   - Detailed metrics and confidence level

### Decision Logic

| Fraud Probability | Decision | Action |
|------------------|----------|---------|
| **>= 0.8** | 🚫 **BLOCK** | Transaction blocked immediately |
| **0.5 - 0.8** | ⚠️ **REVIEW** | Flagged for manual review |
| **< 0.5** | ✅ **ALLOW** | Transaction approved |

### Using the API Directly

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Make Prediction:**
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

## 📁 Project Structure

```
creadit-card-fraud/
├── backend_api.py              # FastAPI backend
├── frontend_app.py             # Streamlit frontend
├── app.py                      # Original Flask API (legacy)
├── requirements.txt            # Dependencies
├── artifacts/
│   ├── xgb_model.pkl          # Trained model
│   ├── preprocessor.pkl       # Preprocessor
│   └── model_metrics.json     # Model metrics
├── src/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_training.py
│   └── pipeline/
│       └── predict_pipeline.py
└── tests/                      # Unit tests
```

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/predict` | POST | Fraud prediction |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation |

---

## 🎯 Example Transactions

### Normal Transaction (Low Risk)
- Amount: $89.50
- Time: 2 PM (business hours)
- Distance: 5.2 km (local)
- Category: Grocery
- **Expected:** ALLOW (probability < 0.2)

### Suspicious Transaction (Medium Risk)
- Amount: $2,500
- Time: 2 AM (late night)
- Distance: 3,944 km (cross-country)
- Transactions in 1h: 8
- **Expected:** REVIEW (probability 0.5-0.8)

### High-Risk Transaction (High Risk)
- Amount: $4,999.99
- Time: 3 AM (late night)
- Distance: 3,876 km (cross-country)
- Transactions in 1h: 15
- Amount deviation: 66x normal
- **Expected:** BLOCK (probability >= 0.8)

---

## 🛠️ Development

### Run Backend with Auto-Reload
```bash
uvicorn backend_api:app --reload --port 8000
```

### Run Tests
```bash
pytest tests/ -v
```

### Access API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔒 Security Notes

- **Production Deployment:**
  - Set specific CORS origins (don't use `*`)
  - Add authentication/authorization
  - Use HTTPS
  - Encrypt credit card data
  - Implement rate limiting

- **PCI DSS Compliance:**
  - Hash or tokenize credit card numbers
  - Implement data retention policies
  - Add audit logging

---

## 📊 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API framework |
| Frontend | Streamlit | Interactive web UI |
| ML Model | XGBoost | Fraud classification |
| Validation | Pydantic | Request validation |
| Server | Uvicorn | ASGI server |

---

## 🐛 Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Ensure model artifacts exist in `artifacts/`
- Verify all dependencies are installed

**Frontend can't connect:**
- Make sure backend is running on port 8000
- Check firewall settings
- Verify API_URL in `frontend_app.py`

**Model not found:**
- Train the model first using the training pipeline
- Check `artifacts/` directory exists

---

## 📈 Future Enhancements

- [ ] User authentication and session management
- [ ] Transaction history dashboard
- [ ] Real-time monitoring and alerts
- [ ] Model retraining pipeline
- [ ] Docker containerization
- [ ] Database integration for transaction storage
- [ ] A/B testing framework for model versions

---

## 👤 Author

**Ganesh**
- Email: tarigondaganesh1234@gmail.com

---

## 📄 License

This project is for educational and demonstration purposes.

---

**🎉 Your fraud detection system is now production-ready!**

Start both servers and access the beautiful web interface at http://localhost:8501
