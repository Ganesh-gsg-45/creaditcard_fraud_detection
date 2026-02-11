import sys
import pandas as pd
import joblib
from src.exception import customException


class PredictPipeline:
    def __init__(self):
        try:
            self.model = joblib.load("artifacts/xgb_model.pkl")
            self.preprocessor = joblib.load("artifacts/preprocessor.pkl")
        except Exception as e:
            raise customException(e, sys)

    def predict(self, input_df: pd.DataFrame):
        try:
            # Ensure input is DataFrame
            if not isinstance(input_df, pd.DataFrame):
                input_df = pd.DataFrame(input_df)

            # Preprocess
            X_processed = self.preprocessor.transform(input_df)

            # Predict probability
            fraud_prob = self.model.predict_proba(X_processed)[:, 1]

            # Binary prediction
            fraud_pred = (fraud_prob >= 0.5).astype(int)

            # Business decision
            decisions = []
            for p in fraud_prob:
                if p >= 0.8:
                    decisions.append("BLOCK")
                elif p >= 0.5:
                    decisions.append("REVIEW")
                else:
                    decisions.append("ALLOW")

            return pd.DataFrame({
                "fraud_probability": fraud_prob,
                "fraud_prediction": fraud_pred,
                "decision": decisions
            })

        except Exception as e:
            raise customException(e, sys)


if __name__ == "__main__":
    # Example single transaction (dummy values – must match schema)
    sample_data = {
        "amt": [120.5],
        "city_pop": [150000],
        "lat": [40.7128],
        "long": [-74.0060],
        "merch_lat": [34.0522],
        "merch_long": [-118.2437],
        "distance_km": [3935],
        "txn_time_gap": [120],
        "txn_count_1h": [3],
        "avg_amt_per_card": [90],
        "amt_deviation": [1.33],
        "customer_age": [32],
        "txn_hour": [23],
        "is_weekend": [1],
        "gender": ["M"],
        "state": ["NY"],
        "category": ["shopping_pos"],
        "merchant": ["fraud_Kirlin and Sons"],
        "cc_num": ["1234567890123456"]
    }

    df = pd.DataFrame(sample_data)

    pipeline = PredictPipeline()
    result = pipeline.predict(df)

    print(result)
