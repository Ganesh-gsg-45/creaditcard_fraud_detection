"""
Example script demonstrating how to use the fraud detection system.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.predict_pipeline import PredictPipeline, CustomData


def example_single_prediction():
    """Example: Make a single fraud prediction."""
    print("=" * 60)
    print("Example 1: Single Transaction Prediction")
    print("=" * 60)
    
    # Create a legitimate-looking transaction
    transaction = CustomData(
        amt=89.50,
        city_pop=150000,
        lat=40.7128,
        long=-74.0060,
        merch_lat=40.7500,
        merch_long=-73.9900,
        distance_km=5.2,
        txn_time_gap=3600.0,  # 1 hour since last transaction
        txn_count_1h=1,
        avg_amt_per_card=95.00,
        amt_deviation=0.94,
        customer_age=35,
        txn_hour=14,  # 2 PM
        is_weekend=0,
        gender='F',
        state='NY',
        category='grocery_pos',
        merchant='Whole Foods',
        cc_num='card_12345'
    )
    
    # Convert to DataFrame and predict
    df = transaction.get_data_as_data_frame()
    pipeline = PredictPipeline()
    result = pipeline.predict(df)
    
    # Display results
    print("\nTransaction Details:")
    print(f"  Amount: ${transaction.amt:.2f}")
    print(f"  Time: {transaction.txn_hour}:00")
    print(f"  Category: {transaction.category}")
    print(f"  Distance: {transaction.distance_km:.1f} km")
    
    print("\nPrediction Results:")
    print(f"  Fraud Probability: {result['fraud_probability'].iloc[0]:.4f}")
    print(f"  Prediction: {'FRAUD' if result['fraud_prediction'].iloc[0] == 1 else 'LEGITIMATE'}")
    print(f"  Decision: {result['decision'].iloc[0]}")
    print()


def example_suspicious_transaction():
    """Example: Predict a suspicious-looking transaction."""
    print("=" * 60)
    print("Example 2: Suspicious Transaction")
    print("=" * 60)
    
    # Create a suspicious transaction
    transaction = CustomData(
        amt=4999.99,  # Very high amount
        city_pop=50000,
        lat=40.7128,
        long=-74.0060,
        merch_lat=34.0522,  # Los Angeles (far away)
        merch_long=-118.2437,
        distance_km=3944.0,  # Cross-country distance
        txn_time_gap=30.0,  # 30 seconds since last transaction
        txn_count_1h=12,  # Many transactions in short time
        avg_amt_per_card=75.00,
        amt_deviation=66.67,  # Huge deviation from normal
        customer_age=22,
        txn_hour=3,  # 3 AM
        is_weekend=1,
        gender='M',
        state='CA',
        category='misc_net',  # Online misc purchase
        merchant='Unknown_Merchant_XYZ',
        cc_num='card_67890'
    )
    
    # Convert to DataFrame and predict
    df = transaction.get_data_as_data_frame()
    pipeline = PredictPipeline()
    result = pipeline.predict(df)
    
    # Display results
    print("\nTransaction Details:")
    print(f"  Amount: ${transaction.amt:.2f} (VERY HIGH)")
    print(f"  Time: {transaction.txn_hour}:00 AM (Late night)")
    print(f"  Distance: {transaction.distance_km:.0f} km (Cross-country)")
    print(f"  Transactions in last hour: {transaction.txn_count_1h}")
    print(f"  Amount deviation: {transaction.amt_deviation:.1f}x normal")
    
    print("\nPrediction Results:")
    print(f"  Fraud Probability: {result['fraud_probability'].iloc[0]:.4f}")
    print(f"  Prediction: {'FRAUD' if result['fraud_prediction'].iloc[0] == 1 else 'LEGITIMATE'}")
    print(f"  Decision: {result['decision'].iloc[0]} ⚠️")
    print()


def example_batch_predictions():
    """Example: Make predictions for multiple transactions."""
    print("=" * 60)
    print("Example 3: Batch Predictions")
    print("=" * 60)
    
    transactions = [
        CustomData(amt=45.00, txn_hour=10, distance_km=2.0),
        CustomData(amt=2500.00, txn_hour=2, distance_km=500.0),
        CustomData(amt=125.00, txn_hour=15, distance_km=10.0),
    ]
    
    pipeline = PredictPipeline()
    
    print(f"\nProcessing {len(transactions)} transactions...\n")
    
    for i, transaction in enumerate(transactions, 1):
        df = transaction.get_data_as_data_frame()
        result = pipeline.predict(df)
        
        print(f"Transaction {i}:")
        print(f"  Amount: ${transaction.amt:.2f}, Time: {transaction.txn_hour}:00")
        print(f"  Decision: {result['decision'].iloc[0]} "
              f"(probability: {result['fraud_probability'].iloc[0]:.4f})")
        print()


def main():
    """Run all examples."""
    print("\n🛡️  Credit Card Fraud Detection - Examples\n")
    
    # Check if model exists
    if not os.path.exists('artifacts/xgb_model.pkl'):
        print("❌ Error: Model not found!")
        print("Please train the model first by running:")
        print("  1. python src/components/data_ingestion.py")
        print("  2. python src/components/data_transformation.py")
        print("  3. python src/components/model_training.py")
        return
    
    try:
        example_single_prediction()
        example_suspicious_transaction()
        example_batch_predictions()
        
        print("=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Trained the model")
        print("  2. All required artifacts in the 'artifacts' folder")


if __name__ == "__main__":
    main()
