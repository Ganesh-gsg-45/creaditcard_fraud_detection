import os
import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from src.exception import customException
from src.logger import logging

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path: str = os.path.join('artifacts', 'preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.config = DataTransformationConfig()

    def get_preprocessor(self):
        try:
            num_features = [
                'amt', 'city_pop', 'lat', 'long', 'merch_lat', 'merch_long',
                'distance_km', 'txn_time_gap', 'txn_count_1h',
                'avg_amt_per_card', 'amt_deviation',
                'customer_age', 'txn_hour', 'is_weekend'
            ]

            low_card_cat = ['gender', 'state', 'category']
            high_card_cat = ['merchant', 'cc_num']

            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', StandardScaler(), num_features),
                    ('low_cat', OneHotEncoder(handle_unknown='ignore'), low_card_cat),
                    ('high_cat', OrdinalEncoder(
                        handle_unknown='use_encoded_value',
                        unknown_value=-1
                    ), high_card_cat)
                ],
                remainder='drop'
            )
            return preprocessor

        except Exception as e:
            raise customException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Train and test data loaded")

            X_train = train_df.drop(columns=['is_fraud'])
            y_train = train_df['is_fraud']

            X_test = test_df.drop(columns=['is_fraud'])
            y_test = test_df['is_fraud']

            preprocessor = self.get_preprocessor()

            X_train_prep = preprocessor.fit_transform(X_train)
            X_test_prep = preprocessor.transform(X_test)

            import joblib
            os.makedirs(os.path.dirname(self.config.preprocessor_obj_file_path), exist_ok=True)
            joblib.dump(preprocessor, self.config.preprocessor_obj_file_path)

            logging.info("Preprocessing completed and object saved")

            # Save transformed arrays for model training using joblib
            import joblib
            os.makedirs('artifacts', exist_ok=True)
            joblib.dump(X_train_prep, os.path.join('artifacts', 'X_train.pkl'))
            joblib.dump(X_test_prep, os.path.join('artifacts', 'X_test.pkl'))
            joblib.dump(y_train.values, os.path.join('artifacts', 'y_train.pkl'))
            joblib.dump(y_test.values, os.path.join('artifacts', 'y_test.pkl'))
            print("Transformed artifacts saved with joblib for model training.")

            return X_train_prep, X_test_prep, y_train, y_test, self.config.preprocessor_obj_file_path

        except Exception as e:
            raise customException(e, sys)

if __name__ == "__main__":
    ingestion_artifacts = os.path.join('artifacts', 'train.csv'), os.path.join('artifacts', 'test.csv')
    transformer = DataTransformation()
    X_train_prep, X_test_prep, y_train, y_test, preprocessor_path = transformer.initiate_data_transformation(*ingestion_artifacts)
    print(f"Preprocessor saved at: {preprocessor_path}")
    print(f"X_train_prep shape: {X_train_prep.shape}")
    print(f"X_test_prep shape: {X_test_prep.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_test shape: {y_test.shape}")
