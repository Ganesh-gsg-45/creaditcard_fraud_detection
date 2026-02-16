"""
Flask REST API for Credit Card Fraud Detection.
Provides endpoints for fraud prediction and health checks.
"""
from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.pipeline.predict_pipeline import PredictPipeline, CustomData
from src.exception import customException
from src.logger import logging
from src.config import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.api.max_content_length


# HTML template for API documentation
API_DOCS_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Credit Card Fraud Detection API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .endpoint { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .method { display: inline-block; padding: 5px 15px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
        .post { background: #49cc90; color: white; }
        .get { background: #61affe; color: white; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .example { margin-top: 10px; }
        h1, h2, h3 { margin-top: 0; }
        .feature-list { columns: 2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Credit Card Fraud Detection API</h1>
        <p>Real-time fraud detection using machine learning</p>
    </div>
    
    <div class="endpoint">
        <h2><span class="method get">GET</span> /</h2>
        <p>API documentation and health check</p>
    </div>
    
    <div class="endpoint">
        <h2><span class="method get">GET</span> /health</h2>
        <p>Check API health status</p>
        <div class="example">
            <strong>Response:</strong>
            <pre>{"status": "healthy", "version": "v1"}</pre>
        </div>
    </div>
    
    <div class="endpoint">
        <h2><span class="method post">POST</span> /predict</h2>
        <p>Make fraud prediction for a transaction</p>
        
        <h3>Required Features:</h3>
        <div class="feature-list">
            <ul>
                <li><code>amt</code> - Transaction amount</li>
                <li><code>city_pop</code> - City population</li>
                <li><code>lat</code> - Customer latitude</li>
                <li><code>long</code> - Customer longitude</li>
                <li><code>merch_lat</code> - Merchant latitude</li>
                <li><code>merch_long</code> - Merchant longitude</li>
                <li><code>distance_km</code> - Distance to merchant</li>
                <li><code>txn_time_gap</code> - Time since last transaction</li>
                <li><code>txn_count_1h</code> - Transactions in last hour</li>
                <li><code>avg_amt_per_card</code> - Average amount per card</li>
                <li><code>amt_deviation</code> - Amount deviation</li>
                <li><code>customer_age</code> - Customer age</li>
                <li><code>txn_hour</code> - Transaction hour (0-23)</li>
                <li><code>is_weekend</code> - Weekend flag (0/1)</li>
                <li><code>gender</code> - Customer gender</li>
                <li><code>state</code> - State code</li>
                <li><code>category</code> - Transaction category</li>
                <li><code>merchant</code> - Merchant name</li>
                <li><code>cc_num</code> - Card number</li>
            </ul>
        </div>
        
        <div class="example">
            <strong>Request Example:</strong>
            <pre>curl -X POST http://localhost:5000/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "amt": 120.0,
    "city_pop": 50000,
    "lat": 40.7,
    "long": -74.0,
    "merch_lat": 40.7,
    "merch_long": -74.0,
    "distance_km": 2.5,
    "txn_time_gap": 30.0,
    "txn_count_1h": 2,
    "avg_amt_per_card": 120.0,
    "amt_deviation": 1.0,
    "customer_age": 45,
    "txn_hour": 14,
    "is_weekend": 0,
    "gender": "M",
    "state": "NY",
    "category": "shopping",
    "merchant": "merchant_1",
    "cc_num": "card_1"
  }'</pre>
        </div>
        
        <div class="example">
            <strong>Success Response:</strong>
            <pre>{
  "success": true,
  "fraud_probability": 0.123,
  "fraud_prediction": 0,
  "decision": "ALLOW",
  "confidence": "high"
}</pre>
        </div>
        
        <div class="example">
            <strong>Error Response:</strong>
            <pre>{
  "success": false,
  "error": "Missing required features: ['amt', 'city_pop']"
}</pre>
        </div>
    </div>
    
    <div class="endpoint">
        <h2>Decision Logic</h2>
        <ul>
            <li><strong>ALLOW</strong>: fraud_probability < 0.5 (legitimate transaction)</li>
            <li><strong>BLOCK</strong>: fraud_probability ≥ 0.5 (suspected fraud)</li>
        </ul>
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def home():
    """API documentation page."""
    return render_template_string(API_DOCS_HTML)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        # Check if model files exist
        import os
        model_exists = os.path.exists(config.model.model_path)
        preprocessor_exists = os.path.exists(config.model.preprocessor_path)
        
        return jsonify({
            'status': 'healthy',
            'version': config.api.api_version,
            'model_loaded': model_exists,
            'preprocessor_loaded': preprocessor_exists
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict fraud for a transaction.
    
    Expects JSON with all required transaction features.
    Returns fraud probability, prediction, and decision.
    """
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        logging.info(f"Received prediction request with {len(data)} features")
        
        # Create CustomData object
        try:
            custom_data = CustomData(**data)
        except TypeError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid or missing fields: {str(e)}'
            }), 400
        
        # Convert to DataFrame
        df = custom_data.get_data_as_data_frame()
        
        # Make prediction
        pipeline = PredictPipeline()
        result = pipeline.predict(df)
        
        # Extract results
        fraud_prob = float(result['fraud_probability'].iloc[0])
        fraud_pred = int(result['fraud_prediction'].iloc[0])
        decision = result['decision'].iloc[0]
        
        # Determine confidence level
        if fraud_prob < 0.2 or fraud_prob > 0.8:
            confidence = 'high'
        elif fraud_prob < 0.4 or fraud_prob > 0.6:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        logging.info(f"Prediction: {decision}, Probability: {fraud_prob:.4f}")
        
        return jsonify({
            'success': True,
            'fraud_probability': round(fraud_prob, 4),
            'fraud_prediction': fraud_pred,
            'decision': decision,
            'confidence': confidence
        })
        
    except ValueError as e:
        # Validation errors (missing features, null values, etc.)
        logging.warning(f"Validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except FileNotFoundError as e:
        # Model not found
        logging.error(f"Model file error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Model not available. Please train the model first.'
        }), 503
        
    except Exception as e:
        # Unexpected errors
        logging.error(f"Prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        'success': False,
        'error': 'Request payload too large'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


if __name__ == '__main__':
    logging.info(f"Starting Flask API on {config.api.host}:{config.api.port}")
    app.run(
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug
    )
