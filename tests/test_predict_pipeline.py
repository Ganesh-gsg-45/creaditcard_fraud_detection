"""
Unit tests for prediction pipeline.
"""
import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.predict_pipeline import PredictPipeline, CustomData


class TestCustomData:
    """Test CustomData class."""
    
    def test_custom_data_creation_with_defaults(self):
        """Test creating CustomData with default values."""
        data = CustomData()
        assert data.amt == 100.0
        assert data.gender == 'M'
        assert data.txn_hour == 12
    
    def test_custom_data_creation_with_params(self, sample_transaction_data):
        """Test creating CustomData with custom parameters."""
        data = CustomData(**sample_transaction_data)
        assert data.amt == 120.0
        assert data.city_pop == 50000
        assert data.gender == 'M'
    
    def test_get_data_as_dataframe(self, sample_transaction_data):
        """Test converting CustomData to DataFrame."""
        data = CustomData(**sample_transaction_data)
        df = data.get_data_as_data_frame()
        
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] == 1  # Single row
        assert 'amt' in df.columns
        assert 'gender' in df.columns
        assert df['amt'].iloc[0] == 120.0
    
    def test_dataframe_has_all_required_features(self, sample_transaction_data):
        """Test that DataFrame contains all required features."""
        data = CustomData(**sample_transaction_data)
        df = data.get_data_as_data_frame()
        
        required_features = [
            'amt', 'city_pop', 'lat', 'long', 'merch_lat', 'merch_long',
            'distance_km', 'txn_time_gap', 'txn_count_1h',
            'avg_amt_per_card', 'amt_deviation', 'customer_age',
            'txn_hour', 'is_weekend', 'gender', 'state', 'category',
            'merchant', 'cc_num'
        ]
        
        for feature in required_features:
            assert feature in df.columns, f"Missing feature: {feature}"


class TestPredictPipeline:
    """Test PredictPipeline class."""
    
    def test_pipeline_initialization(self):
        """Test pipeline can be initialized."""
        pipeline = PredictPipeline()
        assert pipeline is not None
    
    def test_validate_input_with_valid_data(self, sample_transaction_df):
        """Test input validation with valid data."""
        pipeline = PredictPipeline()
        # Should not raise any exception
        pipeline._validate_input(sample_transaction_df)
    
    def test_validate_input_with_missing_features(self):
        """Test input validation catches missing features."""
        pipeline = PredictPipeline()
        invalid_df = pd.DataFrame({'amt': [100.0]})  # Missing most features
        
        with pytest.raises(ValueError, match="Missing required features"):
            pipeline._validate_input(invalid_df)
    
    def test_validate_input_with_null_values(self, sample_transaction_df):
        """Test input validation catches null values."""
        pipeline = PredictPipeline()
        df_with_nulls = sample_transaction_df.copy()
        df_with_nulls.loc[0, 'amt'] = None
        
        with pytest.raises(ValueError, match="null values"):
            pipeline._validate_input(df_with_nulls)
    
    @pytest.mark.skipif(
        not os.path.exists('artifacts/xgb_model.pkl'),
        reason="Model not trained yet"
    )
    def test_prediction_output_format(self, sample_transaction_df):
        """Test prediction returns correct format."""
        pipeline = PredictPipeline()
        result = pipeline.predict(sample_transaction_df)
        
        assert isinstance(result, pd.DataFrame)
        assert 'fraud_probability' in result.columns
        assert 'fraud_prediction' in result.columns
        assert 'decision' in result.columns
        
        # Check value ranges
        assert 0 <= result['fraud_probability'].iloc[0] <= 1
        assert result['fraud_prediction'].iloc[0] in [0, 1]
        assert result['decision'].iloc[0] in ['ALLOW', 'BLOCK']
    
    @pytest.mark.skipif(
        not os.path.exists('artifacts/xgb_model.pkl'),
        reason="Model not trained yet"
    )
    def test_prediction_consistency(self, sample_transaction_df):
        """Test that same input gives same prediction."""
        pipeline = PredictPipeline()
        result1 = pipeline.predict(sample_transaction_df)
        result2 = pipeline.predict(sample_transaction_df)
        
        assert result1['fraud_probability'].iloc[0] == result2['fraud_probability'].iloc[0]
        assert result1['decision'].iloc[0] == result2['decision'].iloc[0]
    
    def test_prediction_without_model(self, sample_transaction_df):
        """Test prediction fails gracefully without model."""
        # Temporarily rename artifacts if they exist
        model_path = 'artifacts/xgb_model.pkl'
        backup_path = 'artifacts/xgb_model.pkl.backup'
        
        model_exists = os.path.exists(model_path)
        if model_exists:
            os.rename(model_path, backup_path)
        
        try:
            pipeline = PredictPipeline()
            with pytest.raises(FileNotFoundError):
                pipeline.predict(sample_transaction_df)
        finally:
            if model_exists:
                os.rename(backup_path, model_path)
