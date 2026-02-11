"""
Pytest configuration and shared fixtures.
"""
import pytest
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        'amt': 120.0,
        'city_pop': 50000,
        'lat': 40.7,
        'long': -74.0,
        'merch_lat': 40.7,
        'merch_long': -74.0,
        'distance_km': 2.5,
        'txn_time_gap': 30.0,
        'txn_count_1h': 2,
        'avg_amt_per_card': 120.0,
        'amt_deviation': 1.0,
        'customer_age': 45,
        'txn_hour': 14,
        'is_weekend': 0,
        'gender': 'M',
        'state': 'NY',
        'category': 'shopping',
        'merchant': 'merchant_1',
        'cc_num': 'card_1'
    }


@pytest.fixture
def sample_transaction_df(sample_transaction_data):
    """Sample transaction as DataFrame."""
    return pd.DataFrame([sample_transaction_data])


@pytest.fixture
def high_risk_transaction_data():
    """High risk transaction for testing."""
    return {
        'amt': 5000.0,  # Very high amount
        'city_pop': 50000,
        'lat': 40.7,
        'long': -74.0,
        'merch_lat': 35.0,  # Far from customer
        'merch_long': -80.0,
        'distance_km': 850.0,  # Very far distance
        'txn_time_gap': 10.0,  # Quick succession
        'txn_count_1h': 15,  # Many transactions
        'avg_amt_per_card': 100.0,
        'amt_deviation': 50.0,  # Large deviation
        'customer_age': 25,
        'txn_hour': 3,  # Late night
        'is_weekend': 1,
        'gender': 'M',
        'state': 'CA',
        'category': 'misc_net',
        'merchant': 'new_merchant_xyz',
        'cc_num': 'card_suspicious'
    }
