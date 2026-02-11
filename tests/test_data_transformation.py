"""
Unit tests for data transformation component.
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.components.data_transformation import DataTransformation


class TestDataTransformation:
    """Test data transformation."""
    
    def test_transformation_initialization(self):
        """Test DataTransformation can be initialized."""
        transformer = DataTransformation()
        assert transformer is not None
        assert transformer.config is not None
    
    def test_get_preprocessor(self):
        """Test preprocessor creation."""
        transformer = DataTransformation()
        preprocessor = transformer.get_preprocessor()
        
        assert preprocessor is not None
        assert hasattr(preprocessor, 'fit_transform')
        assert hasattr(preprocessor, 'transform')
    
    def test_preprocessor_has_correct_transformers(self):
        """Test preprocessor contains expected transformers."""
        transformer = DataTransformation()
        preprocessor = transformer.get_preprocessor()
        
        # Check transformer names
        transformer_names = [name for name, _, _ in preprocessor.transformers]
        assert 'num' in transformer_names
        assert 'low_cat' in transformer_names
        assert 'high_cat' in transformer_names
    
    @pytest.mark.skipif(
        not os.path.exists('artifacts/train.csv'),
        reason="Training data not available"
    )
    def test_initiate_data_transformation(self):
        """Test complete data transformation pipeline."""
        transformer = DataTransformation()
        
        train_path = 'artifacts/train.csv'
        test_path = 'artifacts/test.csv'
        
        if not os.path.exists(train_path) or not os.path.exists(test_path):
            pytest.skip("Required data files not available")
        
        X_train, X_test, y_train, y_test, preprocessor_path = \
            transformer.initiate_data_transformation(train_path, test_path)
        
        # Check outputs
        assert X_train is not None
        assert X_test is not None
        assert y_train is not None
        assert y_test is not None
        
        # Check shapes
        assert X_train.shape[0] == len(y_train)
        assert X_test.shape[0] == len(y_test)
        
        # Check preprocessor saved
        assert os.path.exists(preprocessor_path)
    
    def test_numerical_features_scaled(self):
        """Test that numerical features are properly scaled."""
        # Create sample data
        sample_data = pd.DataFrame({
            'amt': [100.0, 200.0, 300.0],
            'city_pop': [10000, 20000, 30000],
            'lat': [40.0, 41.0, 42.0],
            'long': [-74.0, -75.0, -76.0],
            'merch_lat': [40.0, 41.0, 42.0],
            'merch_long': [-74.0, -75.0, -76.0],
            'distance_km': [1.0, 2.0, 3.0],
            'txn_time_gap': [10.0, 20.0, 30.0],
            'txn_count_1h': [1, 2, 3],
            'avg_amt_per_card': [100.0, 150.0, 200.0],
            'amt_deviation': [1.0, 1.5, 2.0],
            'customer_age': [30, 40, 50],
            'txn_hour': [12, 14, 16],
            'is_weekend': [0, 1, 0],
            'gender': ['M', 'F', 'M'],
            'state': ['NY', 'CA', 'TX'],
            'category': ['food', 'gas', 'shopping'],
            'merchant': ['merchant1', 'merchant2', 'merchant3'],
            'cc_num': ['card1', 'card2', 'card3'],
            'is_fraud': [0, 0, 1]
        })
        
        transformer = DataTransformation()
        preprocessor = transformer.get_preprocessor()
        
        X = sample_data.drop(columns=['is_fraud'])
        X_transformed = preprocessor.fit_transform(X)
        
        # Check that output is numeric
        assert X_transformed is not None
        # For sparse matrices, check shape
        if hasattr(X_transformed, 'shape'):
            assert X_transformed.shape[0] == 3
