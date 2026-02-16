# 🛡️ Credit Card Fraud Detection System

A full-stack Machine Learning application for real-time credit card fraud detection with intelligent risk assessment.

## ✨ Features

- **Real-time Fraud Detection** - Instant transaction analysis using XGBoost ML model
- **3-Tier Decision System** - ALLOW, REVIEW, or BLOCK transactions based on risk
- **Interactive Web Interface** - Beautiful Streamlit dashboard with example templates
- **REST API** - FastAPI backend with automatic documentation
- **Transaction History** - View analytics and fraud statistics (with Supabase integration)
- **Advanced ML Features** - Transaction velocity, spending patterns, distance analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Train the model** (first time only):
```bash
python src/components/data_ingestion.py
python src/components/data_transformation.py
python src/components/model_training.py
```

3. **Run the application**:

**Terminal 1 - Backend API**:
```bash
python backend_api.py
```

**Terminal 2 - Frontend**:
```bash
streamlit run app.py
```

4. **Open your browser** to `http://localhost:8501`

## 📖 How to Use

### Web Interface
1. Select a transaction example (Normal, Suspicious, or High-Risk)
2. Adjust transaction details if needed
3. Click "Analyze Transaction"
4. View the fraud risk assessment and decision

### API Usage
Access the API documentation at `http://localhost:8000/docs`

**Example Request**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amt": 120.50,
    "category": "grocery_pos",
    "merchant": "Whole Foods",
    "customer_age": 35,
    "txn_hour": 14,
    "is_weekend": 0,
    "gender": "M",
    "state": "NY",
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
    "cc_num": "card_12345"
  }'
```

## 📁 Project Structure

```
├── src/
│   ├── components/          # Data processing & model training
│   ├── pipeline/            # Prediction pipeline
│   └── services/            # Database service
├── tests/                   # Test suite
├── artifacts/               # Trained models
├── app.py                  # Streamlit frontend
├── backend_api.py          # FastAPI backend
└── requirements.txt        # Dependencies
```

## 🧪 Testing

```bash
pytest                      # Run all tests
pytest --cov=src           # Run with coverage
```

## 🔧 Technology Stack

- **Machine Learning**: XGBoost, Scikit-learn
- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Database**: Supabase (optional)
- **Testing**: Pytest

## 💾 Database Setup (Optional)

To enable transaction history and analytics:

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project
3. Create a `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```
4. Run the SQL scripts in `database/` folder to create tables
5. Restart the backend

## 👤 Author

**Ganesh**  
Email: tarigondaganesh1234@gmail.com

## � License

Educational and research purposes.

---

**Version 2.0** | Built with ❤️ using Machine Learning
