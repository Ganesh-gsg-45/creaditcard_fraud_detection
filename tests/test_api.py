"""
Integration tests for Flask API.
"""
import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Test Flask API endpoints."""
    
    def test_home_endpoint(self, client):
        """Test home endpoint returns documentation."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Credit Card Fraud Detection API' in response.data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['healthy', 'unhealthy']
        assert 'version' in data
    
    def test_predict_endpoint_missing_data(self, client):
        """Test predict endpoint with no data."""
        response = client.post('/predict')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_predict_endpoint_invalid_json(self, client):
        """Test predict endpoint with invalid JSON."""
        response = client.post(
            '/predict',
            data='not json',
            content_type='text/plain'
        )
        assert response.status_code == 400
    
    def test_predict_endpoint_missing_features(self, client):
        """Test predict endpoint with missing features."""
        incomplete_data = {
            'amt': 100.0,
            'city_pop': 50000
            # Missing most required features
        }
        
        response = client.post(
            '/predict',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    @pytest.mark.skipif(
        not os.path.exists('artifacts/xgb_model.pkl'),
        reason="Model not trained yet"
    )
    def test_predict_endpoint_valid_request(self, client, sample_transaction_data):
        """Test predict endpoint with valid data."""
        response = client.post(
            '/predict',
            data=json.dumps(sample_transaction_data),
            content_type='application/json'
        )
        
        # Should succeed if model is available
        if os.path.exists('artifacts/xgb_model.pkl'):
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'fraud_probability' in data
            assert 'fraud_prediction' in data
            assert 'decision' in data
            assert 'confidence' in data
            
            # Validate values
            assert 0 <= data['fraud_probability'] <= 1
            assert data['fraud_prediction'] in [0, 1]
            assert data['decision'] in ['ALLOW', 'BLOCK']
            assert data['confidence'] in ['low', 'medium', 'high']
    
    def test_predict_endpoint_without_model(self, client, sample_transaction_data):
        """Test predict endpoint fails gracefully without model."""
        # If model doesn't exist, should return 503
        if not os.path.exists('artifacts/xgb_model.pkl'):
            response = client.post(
                '/predict',
                data=json.dumps(sample_transaction_data),
                content_type='application/json'
            )
            assert response.status_code == 503
            
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Model not available' in data['error']
    
    def test_404_error_handler(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_large_payload_rejection(self, client):
        """Test that very large payloads are rejected."""
        # Create a large payload (>16MB)
        large_data = {'amt': 100.0}
        large_data['large_field'] = 'x' * (17 * 1024 * 1024)  # 17MB
        
        response = client.post(
            '/predict',
            data=json.dumps(large_data),
            content_type='application/json'
        )
        assert response.status_code == 413


class TestAPIResponseFormat:
    """Test API response formats."""
    
    @pytest.mark.skipif(
        not os.path.exists('artifacts/xgb_model.pkl'),
        reason="Model not trained yet"
    )
    def test_success_response_format(self, client, sample_transaction_data):
        """Test successful prediction response format."""
        response = client.post(
            '/predict',
            data=json.dumps(sample_transaction_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            # Check all required fields present
            required_fields = ['success', 'fraud_probability', 'fraud_prediction', 'decision', 'confidence']
            for field in required_fields:
                assert field in data, f"Missing field: {field}"
            
            # Check data types
            assert isinstance(data['success'], bool)
            assert isinstance(data['fraud_probability'], (int, float))
            assert isinstance(data['fraud_prediction'], int)
            assert isinstance(data['decision'], str)
            assert isinstance(data['confidence'], str)
    
    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.post('/predict')
        data = json.loads(response.data)
        
        # Error responses should have success=False and error message
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert isinstance(data['error'], str)
