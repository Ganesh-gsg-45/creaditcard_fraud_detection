import sys
import pandas as pd
import joblib
from src.exception import customException


class predictpipeline:
    def __init__(self):
        pass

    def predict(self, features: pd.DataFrame):
        try:
            # prefer the model we saved during training; fall back to model.pkl if present
            model_candidates = ["artifacts/xgb_model.pkl", "artifacts/model.pkl"]
            preprocessor_candidates = ["artifacts/preprocessor.pkl"]

            model = None
            for p in model_candidates:
                try:
                    model = joblib.load(p)
                    model_path = p
                    break
                except Exception:
                    continue
            if model is None:
                raise FileNotFoundError("No model file found in artifacts (tried {}).".format(model_candidates))

            preprocessor = None
            for p in preprocessor_candidates:
                try:
                    preprocessor = joblib.load(p)
                    preprocessor_path = p
                    break
                except Exception:
                    continue
            if preprocessor is None:
                raise FileNotFoundError("No preprocessor file found in artifacts (tried {}).".format(preprocessor_candidates))

            # Ensure input is a DataFrame
            if not isinstance(features, pd.DataFrame):
                features = pd.DataFrame(features)

            # transform and predict
            data_scaled = preprocessor.transform(features)

            # get predicted probability for positive class (1)
            prob = None
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(data_scaled)[:, 1]
            elif hasattr(model, 'decision_function'):
                # fallback: map decision_function to (0,1) via sigmoid
                from scipy.special import expit
                scores = model.decision_function(data_scaled)
                prob = expit(scores)
            else:
                # final fallback: use predicted labels as 0/1 probabilities
                preds = model.predict(data_scaled)
                prob = preds.astype(float)

            preds = (prob >= 0.5).astype(int)

            # Build result DataFrame
            result = pd.DataFrame({
                'fraud_probability': prob,
                'fraud_prediction': preds,
            })
            # Decision: BLOCK if predicted fraud (1), else ALLOW
            result['decision'] = result['fraud_prediction'].map({0: 'ALLOW', 1: 'BLOCK'})

            return result
        except Exception as e:
            raise customException(e, sys)


class CustomData:
    """Construct a single-row DataFrame containing all features expected by the preprocessor.

    Fields chosen to match transformed features used in this project.
    """
    def __init__(
        self,
        amt: float = 100.0,
        city_pop: float = 100000.0,
        lat: float = 40.0,
        long: float = -73.0,
        merch_lat: float = 40.0,
        merch_long: float = -73.0,
        distance_km: float = 1.0,
        txn_time_gap: float = 0.0,
        txn_count_1h: int = 1,
        avg_amt_per_card: float = 100.0,
        amt_deviation: float = 0.0,
        customer_age: int = 30,
        txn_hour: int = 12,
        is_weekend: int = 0,
        gender: str = 'M',
        state: str = 'NY',
        category: str = 'shopping',
        merchant: str = 'merchant_1',
        cc_num: str = 'card_1',
    ):
        self.amt = amt
        self.city_pop = city_pop
        self.lat = lat
        self.long = long
        self.merch_lat = merch_lat
        self.merch_long = merch_long
        self.distance_km = distance_km
        self.txn_time_gap = txn_time_gap
        self.txn_count_1h = txn_count_1h
        self.avg_amt_per_card = avg_amt_per_card
        self.amt_deviation = amt_deviation
        self.customer_age = customer_age
        self.txn_hour = txn_hour
        self.is_weekend = is_weekend
        self.gender = gender
        self.state = state
        self.category = category
        self.merchant = merchant
        self.cc_num = cc_num

    def get_data_as_data_frame(self) -> pd.DataFrame:
        try:
            data = {
                'amt': [self.amt],
                'city_pop': [self.city_pop],
                'lat': [self.lat],
                'long': [self.long],
                'merch_lat': [self.merch_lat],
                'merch_long': [self.merch_long],
                'distance_km': [self.distance_km],
                'txn_time_gap': [self.txn_time_gap],
                'txn_count_1h': [self.txn_count_1h],
                'avg_amt_per_card': [self.avg_amt_per_card],
                'amt_deviation': [self.amt_deviation],
                'customer_age': [self.customer_age],
                'txn_hour': [self.txn_hour],
                'is_weekend': [self.is_weekend],
                'gender': [self.gender],
                'state': [self.state],
                'category': [self.category],
                'merchant': [self.merchant],
                'cc_num': [self.cc_num],
            }
            return pd.DataFrame(data)
        except Exception as e:
            raise customException(e, sys)


if __name__ == "__main__":
    try:
        example = CustomData(
            amt=120.0,
            city_pop=50000.0,
            lat=40.7,
            long=-74.0,
            merch_lat=40.7,
            merch_long=-74.0,
            distance_km=2.5,
            txn_time_gap=30.0,
            txn_count_1h=2,
            avg_amt_per_card=120.0,
            amt_deviation=10.0,
            customer_age=45,
            txn_hour=14,
            is_weekend=0,
            gender='M',
            state='NY',
            category='shopping',
            merchant='merchant_1',
            cc_num='card_1',
        )
        df = example.get_data_as_data_frame()
        preds = predictpipeline().predict(df)
        print('Prediction:', preds)
    except Exception as e:
        msg = str(e)
        if 'columns are missing' in msg:
            print('Error: input DataFrame is missing required feature columns.')
            print(msg)
            print('\nMake sure to pass a DataFrame with all features produced by the data transformation step.')
        else:
            print('Error running predict pipeline:', e)
