"""
FastAPI Backend for Credit Card Fraud Detection System
Production-ready API with Pydantic validation and 3-tier decision logic
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import joblib
import pandas as pd
import numpy as np
from typing import Literal, Optional, Dict, List, Any
import os
import logging
from dotenv import load_dotenv
from src.services.database_service import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Card Fraud Detection API",
    description="Real-time fraud detection using XGBoost ML model",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and preprocessor at startup
MODEL_PATH = "artifacts/xgb_model.pkl"
PREPROCESSOR_PATH = "artifacts/preprocessor.pkl"

model = None
preprocessor = None
db_service: Optional[DatabaseService] = None

@app.on_event("startup")
async def load_artifacts():
    """Load model, preprocessor, and initialize database service on startup."""
    global model, preprocessor, db_service
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info(f"✅ Model loaded from {MODEL_PATH}")
        else:
            logger.warning(f"⚠️  Model not found at {MODEL_PATH}")
        
        if os.path.exists(PREPROCESSOR_PATH):
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            logger.info(f"✅ Preprocessor loaded from {PREPROCESSOR_PATH}")
        else:
            logger.warning(f"⚠️  Preprocessor not found at {PREPROCESSOR_PATH}")
        
        # Initialize Supabase database service
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            try:
                db_service = DatabaseService(supabase_url, supabase_key)
                logger.info("✅ Database service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize database service: {e}")
                db_service = None
        else:
            logger.warning("⚠️  Supabase credentials not found in environment variables")
            
    except Exception as e:
        logger.error(f"❌ Error loading artifacts: {e}")


# Pydantic Models
class TransactionRequest(BaseModel):
    """Transaction data for fraud prediction."""
    amt: float = Field(..., gt=0, description="Transaction amount in USD")
    city_pop: float = Field(..., ge=0, description="City population")
    lat: float = Field(..., ge=-90, le=90, description="Customer latitude")
    long: float = Field(..., ge=-180, le=180, description="Customer longitude")
    merch_lat: float = Field(..., ge=-90, le=90, description="Merchant latitude")
    merch_long: float = Field(..., ge=-180, le=180, description="Merchant longitude")
    distance_km: float = Field(..., ge=0, description="Distance to merchant in km")
    txn_time_gap: float = Field(..., ge=0, description="Time since last transaction (seconds)")
    txn_count_1h: int = Field(..., ge=0, description="Transaction count in last hour")
    avg_amt_per_card: float = Field(..., ge=0, description="Average amount per card")
    amt_deviation: float = Field(..., ge=0, description="Amount deviation from average")
    customer_age: int = Field(..., ge=18, le=120, description="Customer age")
    txn_hour: int = Field(..., ge=0, le=23, description="Transaction hour (0-23)")
    is_weekend: int = Field(..., ge=0, le=1, description="Weekend flag (0 or 1)")
    gender: Literal["M", "F"] = Field(..., description="Customer gender")
    state: str = Field(..., min_length=2, max_length=2, description="US state code")
    category: str = Field(..., description="Transaction category")
    merchant: str = Field(..., description="Merchant name")
    cc_num: str = Field(..., description="Credit card number (hashed/tokenized)")

    class Config:
        schema_extra = {
            "example": {
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
            }
        }


class PredictionResponse(BaseModel):
    """Fraud prediction response."""
    fraud_probability: float = Field(..., description="Probability of fraud (0-1)")
    fraud_prediction: int = Field(..., description="Binary prediction (0=legit, 1=fraud)")
    decision: Literal["ALLOW", "REVIEW", "BLOCK"] = Field(..., description="Final decision")
    confidence: str = Field(..., description="Confidence level")
    message: str = Field(..., description="Human-readable message")


# API Endpoints
@app.get("/")
async def root():
    """API information."""
    return {
        "name": "Credit Card Fraud Detection API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/health": "Health check",
            "/predict": "Fraud prediction (POST)",
            "/docs": "API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = db_service.health_check() if db_service else False
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "database_connected": db_healthy,
        "model_path": MODEL_PATH,
        "preprocessor_path": PREPROCESSOR_PATH
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: TransactionRequest):
    """
    Predict fraud for a transaction.
    
    Decision Logic:
    - Probability >= 0.8 → BLOCK
    - Probability >= 0.5 → REVIEW  
    - Probability < 0.5 → ALLOW
    """
    try:
        # Check if artifacts are loaded
        if model is None or preprocessor is None:
            raise HTTPException(
                status_code=503,
                detail="Model or preprocessor not loaded. Please train the model first."
            )
        
        # Convert to DataFrame
        transaction_dict = transaction.dict()
        df = pd.DataFrame([transaction_dict])
        
        logger.info(f"Processing transaction: amount=${transaction.amt:.2f}, hour={transaction.txn_hour}")
        
        # Preprocess
        X_processed = preprocessor.transform(df)
        
        # Predict
        fraud_prob = float(model.predict_proba(X_processed)[0, 1])
        fraud_pred = int(fraud_prob >= 0.5)
        
        # 3-Tier Decision Logic
        if fraud_prob >= 0.8:
            decision = "BLOCK"
            message = "🚫 Transaction BLOCKED - High fraud risk detected"
            confidence = "high"
        elif fraud_prob >= 0.5:
            decision = "REVIEW"
            message = "⚠️  Transaction flagged for REVIEW - Moderate fraud risk"
            confidence = "medium"
        else:
            decision = "ALLOW"
            message = "✅ Transaction ALLOWED - Low fraud risk"
            confidence = "high" if fraud_prob < 0.2 else "medium"
        
        logger.info(f"Prediction: {decision} (probability={fraud_prob:.4f})")
        
        # Log transaction to database
        if db_service:
            try:
                # Prepare transaction data for database
                db_transaction = {
                    'amt': transaction.amt,
                    'category': transaction.category,
                    'merchant': transaction.merchant,
                    'state': transaction.state,
                    'customer_age': transaction.customer_age,
                    'fraud_probability': round(fraud_prob, 4),
                    'fraud_prediction': fraud_pred,
                    'decision': decision,
                    'city_pop': transaction.city_pop,
                    'lat': transaction.lat,
                    'long': transaction.long,
                    'merch_lat': transaction.merch_lat,
                    'merch_long': transaction.merch_long,
                    'distance_km': transaction.distance_km,
                    'txn_time_gap': transaction.txn_time_gap,
                    'txn_count_1h': transaction.txn_count_1h,
                    'avg_amt_per_card': transaction.avg_amt_per_card,
                    'amt_deviation': transaction.amt_deviation,
                    'txn_hour': transaction.txn_hour,
                    'is_weekend': transaction.is_weekend,
                    'gender': transaction.gender,
                    'cc_num': transaction.cc_num
                }
                
                # Insert transaction
                inserted_transaction = db_service.log_transaction(db_transaction)
                
                # If BLOCK or REVIEW, also flag the transaction
                if decision in ["BLOCK", "REVIEW"] and inserted_transaction:
                    risk_level = "CRITICAL" if decision == "BLOCK" else "HIGH"
                    db_service.log_flagged_transaction(
                        inserted_transaction['id'], 
                        risk_level
                    )
                    
            except Exception as e:
                logger.error(f"❌ Database logging failed: {e}")
                # Continue even if logging fails
        
        return PredictionResponse(
            fraud_probability=round(fraud_prob, 4),
            fraud_prediction=fraud_pred,
            decision=decision,
            confidence=confidence,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/transactions/history")
async def get_transaction_history(limit: int = 20):
    """
    Get recent transaction history.
    
    Args:
        limit: Maximum number of transactions to retrieve (default: 20)
    
    Returns:
        List of recent transactions
    """
    try:
        if not db_service:
            raise HTTPException(
                status_code=503,
                detail="Database service not available"
            )
        
        transactions = db_service.get_recent_transactions(limit)
        return {
            "count": len(transactions),
            "transactions": transactions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions/stats")
async def get_fraud_statistics():
    """
    Get fraud detection statistics.
    
    Returns:
        Fraud statistics including total transactions, fraud rate, etc.
    """
    try:
        if not db_service:
            raise HTTPException(
                status_code=503,
                detail="Database service not available"
            )
        
        stats = db_service.get_fraud_statistics()
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get fraud statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions/flagged")
async def get_flagged_transactions(limit: int = 50):
    """
    Get flagged transactions (BLOCK/REVIEW decisions).
    
    Args:
        limit: Maximum number of flagged transactions to retrieve (default: 50)
    
    Returns:
        List of flagged transactions with details
    """
    try:
        if not db_service:
            raise HTTPException(
                status_code=503,
                detail="Database service not available"
            )
        
        flagged = db_service.get_flagged_transactions(limit)
        return {
            "count": len(flagged),
            "flagged_transactions": flagged
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get flagged transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
