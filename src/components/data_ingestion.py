import os
import sys

# Ensure src is in sys.path for local script execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from dataclasses import dataclass
from sklearn.model_selection import train_test_split

from src.exception import customException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    train_data_path: str = os.path.join('artifacts', "train.csv")
    test_data_path: str = os.path.join('artifacts', "test.csv")
    raw_data_path: str = os.path.join('artifacts', "raw.csv")


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def haversine(self, lat1, lon1, lat2, lon2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return 6371  * c  # distance in km

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion")
        try:
            df = pd.read_csv(os.path.join('data', 'fraudTrain.csv'))
            logging.info("Dataset loaded successfully")

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path, index=False)

            # Drop non-informative / personal columns
            drop_cols = ['Unnamed: 0', 'first', 'last', 'street', 'city', 'trans_num', 'zip']
            df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

            # Convert datetime columns
            df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
            df['dob'] = pd.to_datetime(df['dob'])

            # Time-based features
            df['txn_hour'] = df['trans_date_trans_time'].dt.hour
            df['txn_dayofweek'] = df['trans_date_trans_time'].dt.dayofweek
            df['is_weekend'] = df['txn_dayofweek'].isin([5, 6]).astype(int)
            df['customer_age'] = ((df['trans_date_trans_time'] - df['dob']).dt.days // 365)

            # Distance feature
            df['distance_km'] = df.apply(
                lambda x: self.haversine(
                    x['lat'], x['long'], x['merch_lat'], x['merch_long']
                ),
                axis=1
            )

            # Sort for time-based features
            df = df.sort_values(['cc_num', 'trans_date_trans_time'])

            # Transaction time gap
            df['txn_time_gap'] = (
                df.groupby('cc_num')['trans_date_trans_time']
                .diff()
                .dt.seconds
                .fillna(0)
            )

            # Rolling transaction count (1 hour)
            df = df.set_index('trans_date_trans_time')
            df['txn_count_1h'] = (
                df.groupby('cc_num')['amt']
                .rolling('1h')
                .count()
                .reset_index(level=0, drop=True)
            )
            df = df.reset_index()

            # Spending behavior (use expanding mean to prevent data leakage)
            # This ensures we only use past transactions, not future ones
            df['avg_amt_per_card'] = df.groupby('cc_num')['amt'].transform(
                lambda x: x.expanding().mean().shift(1)
            ).fillna(df['amt'].median())
            df['amt_deviation'] = df['amt'] / (df['avg_amt_per_card'] + 1)

            # New merchant flag
            df['is_new_merchant'] = (
                df.groupby('cc_num')['merchant']
                .transform(lambda x: ~x.duplicated())
                .astype(int)
            )

            # Drop raw columns after feature extraction
            df.drop(columns=['trans_date_trans_time', 'unix_time', 'dob'], inplace=True)

            # Train-test split
            train_set, test_set = train_test_split(
                df,
                test_size=0.2,
                stratify=df['is_fraud'],
                random_state=42
            )

            train_set.to_csv(self.ingestion_config.train_data_path, index=False)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False)

            logging.info("Data ingestion completed successfully")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )

        except Exception as e:
            raise customException(e, sys)


if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()
