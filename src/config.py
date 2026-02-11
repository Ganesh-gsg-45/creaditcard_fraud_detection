"""
Configuration management for Credit Card Fraud Detection System.
Centralized settings for paths, model parameters, and API configuration.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DataConfig:
    """Data-related configuration."""
    raw_data_path: str = os.path.join('data', 'fraudTrain.csv')
    artifacts_dir: str = 'artifacts'
    train_data_path: str = os.path.join(artifacts_dir, 'train.csv')
    test_data_path: str = os.path.join(artifacts_dir, 'test.csv')
    raw_artifact_path: str = os.path.join(artifacts_dir, 'raw.csv')


@dataclass
class ModelConfig:
    """Model training configuration."""
    model_name: str = 'xgboost'
    model_path: str = os.path.join('artifacts', 'xgb_model.pkl')
    preprocessor_path: str = os.path.join('artifacts', 'preprocessor.pkl')
    metrics_path: str = os.path.join('artifacts', 'model_metrics.json')
    
    # XGBoost hyperparameters
    n_estimators: int = 300
    max_depth: int = 6
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    random_state: int = 42
    eval_metric: str = 'logloss'


@dataclass
class PredictionConfig:
    """Prediction and fraud detection configuration."""
    fraud_probability_threshold: float = 0.5
    high_risk_amount: float = 1000.0
    
    # Required features for prediction
    required_features: list = None
    
    def __post_init__(self):
        if self.required_features is None:
            self.required_features = [
                'amt', 'city_pop', 'lat', 'long', 'merch_lat', 'merch_long',
                'distance_km', 'txn_time_gap', 'txn_count_1h',
                'avg_amt_per_card', 'amt_deviation', 'customer_age',
                'txn_hour', 'is_weekend', 'gender', 'state', 'category',
                'merchant', 'cc_num'
            ]


@dataclass
class APIConfig:
    """Flask API configuration."""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = True
    api_version: str = 'v1'
    max_content_length: int = 16 * 1024 * 1024  # 16MB max request size


class Config:
    """Main configuration class combining all configs."""
    
    def __init__(self):
        self.data = DataConfig()
        self.model = ModelConfig()
        self.prediction = PredictionConfig()
        self.api = APIConfig()
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables if available."""
        config = cls()
        
        # Override with environment variables if they exist
        config.api.host = os.getenv('API_HOST', config.api.host)
        config.api.port = int(os.getenv('API_PORT', config.api.port))
        config.api.debug = os.getenv('API_DEBUG', 'True').lower() == 'true'
        
        # Prediction threshold from environment
        threshold = os.getenv('FRAUD_THRESHOLD')
        if threshold:
            config.prediction.fraud_probability_threshold = float(threshold)
        
        return config


# Global config instance
config = Config.from_env()
