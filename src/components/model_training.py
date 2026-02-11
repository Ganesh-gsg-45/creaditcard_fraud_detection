import os
import sys
import json
from dataclasses import dataclass
import joblib
import numpy as np
from scipy.sparse import vstack, issparse

from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_curve
)

from src.exception import customException
from src.logger import logging


@dataclass
class ModelTrainerConfig:
    model_path: str = os.path.join("artifacts", "xgb_model.pkl")


class ModelTrainer:
    def __init__(self):
        self.config = ModelTrainerConfig()

    def initiate_model_trainer(self, X_train, y_train, X_test, y_test):
        try:
            logging.info("🚀 Starting XGBoost model training")

            # Helper to normalize inputs: accept scipy sparse, numpy arrays,
            # object arrays containing sparse rows (or 0-d wrappers), or lists.
            def _prepare_input(X, name):
                if X is None:
                    return X
                logging.info(f"Preparing {name}: type={type(X)}, dtype={getattr(X, 'dtype', None)}, shape={getattr(X, 'shape', None)}")

                # already a scipy sparse matrix
                if issparse(X):
                    logging.info(f"{name} is scipy sparse — OK to use as-is")
                    return X

                # numpy array
                if isinstance(X, np.ndarray):
                    # object array cases
                    if X.dtype == object:
                        # 0-d wrapper
                        if getattr(X, 'ndim', None) == 0:
                            elem = X.item()
                            if elem is None:
                                return X
                            if issparse(elem):
                                logging.info(f"Unwrapping 0-d object array for {name} (sparse element)")
                                return elem
                            if isinstance(elem, np.ndarray):
                                logging.info(f"Unwrapping 0-d object array for {name} (ndarray element)")
                                return elem

                        # iterable object array of rows
                        # detect whether elements are sparse-like or array-like
                        elems = list(X.flat)
                        if len(elems) == 0:
                            return np.empty((0, 0))

                        if all(e is None for e in elems):
                            return X

                        # if elements are sparse matrices, stack into one sparse matrix
                        if all((e is None) or issparse(e) or hasattr(e, 'toarray') for e in elems):
                            logging.info(f"Stacking object-array of sparse rows for {name}")
                            sparse_rows = [e for e in elems if e is not None]
                            return vstack(sparse_rows)

                        # if elements are array-like, try vstack to dense
                        try:
                            logging.info(f"Stacking object-array of array-like rows for {name}")
                            return np.vstack(elems)
                        except Exception:
                            logging.info(f"Could not vstack object-array for {name}; falling back to original")
                            return X

                    # numeric ndarray — ensure 2D
                    if X.ndim == 1:
                        return X.reshape(-1, 1)
                    return X

                # list/tuple of rows
                if isinstance(X, (list, tuple)):
                    if len(X) == 0:
                        return np.empty((0, 0))
                    # detect sparse-like elements
                    if all(issparse(e) or hasattr(e, 'toarray') for e in X):
                        return vstack([e for e in X])
                    return np.vstack(X)

                # unknown type — return as-is
                return X

            X_train = _prepare_input(X_train, 'X_train')
            X_test = _prepare_input(X_test, 'X_test')

            # Handle extreme class imbalance
            scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

            model = XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1
            )

            # XGBoost can handle scipy sparse matrices or dense numpy arrays.
            logging.info(f"Fitting model with X_train type={type(X_train)}, shape={getattr(X_train, 'shape', None)}")
            model.fit(X_train, y_train)
            logging.info(" Model training completed")

            # Predictions
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]

            # Comprehensive Evaluation
            roc_auc = roc_auc_score(y_test, y_prob)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            # Threshold optimization
            precisions, recalls, thresholds = precision_recall_curve(y_test, y_prob)
            # Find threshold where recall >= 0.90 (catching 90% of fraud)
            target_recall_idx = np.where(recalls >= 0.90)[0]
            if len(target_recall_idx) > 0:
                optimal_threshold = thresholds[target_recall_idx[-1]]
                optimal_precision = precisions[target_recall_idx[-1]]
            else:
                optimal_threshold = 0.5
                optimal_precision = precision
            
            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True)
            
            # Log metrics
            logging.info(f"\n{'='*50}")
            logging.info(f"📊 Model Evaluation Metrics")
            logging.info(f"{'='*50}")
            logging.info(f"ROC-AUC Score: {roc_auc:.4f}")
            logging.info(f"Precision: {precision:.4f}")
            logging.info(f"Recall: {recall:.4f}")
            logging.info(f"F1-Score: {f1:.4f}")
            logging.info(f"\nConfusion Matrix:")
            logging.info(f"  True Negatives:  {tn:,}")
            logging.info(f"  False Positives: {fp:,}")
            logging.info(f"  False Negatives: {fn:,}")
            logging.info(f"  True Positives:  {tp:,}")
            logging.info(f"\nOptimal Threshold (90% recall): {optimal_threshold:.4f}")
            logging.info(f"Precision at 90% recall: {optimal_precision:.4f}")
            logging.info(f"{'='*50}\n")
            
            # Save metrics to JSON
            metrics = {
                'roc_auc': float(roc_auc),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'confusion_matrix': {
                    'true_negatives': int(tn),
                    'false_positives': int(fp),
                    'false_negatives': int(fn),
                    'true_positives': int(tp)
                },
                'optimal_threshold': float(optimal_threshold),
                'optimal_precision_at_90_recall': float(optimal_precision),
                'classification_report': report
            }
            
            metrics_path = os.path.join('artifacts', 'model_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logging.info(f"📁 Metrics saved at: {metrics_path}")
            
            # Save model
            os.makedirs(os.path.dirname(self.config.model_path), exist_ok=True)
            joblib.dump(model, self.config.model_path)
            logging.info(f"💾 Model saved at: {self.config.model_path}")

            return metrics, self.config.model_path

        except Exception as e:
            raise customException(e, sys)


if __name__ == "__main__":
    try:
        import joblib
        X_train = joblib.load("artifacts/X_train.pkl")
        X_test = joblib.load("artifacts/X_test.pkl")
        y_train = joblib.load("artifacts/y_train.pkl")
        y_test = joblib.load("artifacts/y_test.pkl")

        print("Loaded shapes:")
        print("X_train type:", type(X_train))
        print("X_train shape:", X_train.shape)
        print("X_test type:", type(X_test))
        print("X_test shape:", X_test.shape)
        print("y_train:", getattr(y_train, 'shape', None))
        print("y_test :", getattr(y_test, 'shape', None))

        trainer = ModelTrainer()
        metrics, model_path = trainer.initiate_model_trainer(
            X_train, y_train, X_test, y_test
        )

        print(f"\n{'='*50}")
        print(f"✅ Training Complete")
        print(f"{'='*50}")
        print(f"Model saved at: {model_path}")
        print(f"\n📊 Key Metrics:")
        print(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"  Precision: {metrics['precision']:.4f}")
        print(f"  Recall: {metrics['recall']:.4f}")
        print(f"  F1-Score: {metrics['f1_score']:.4f}")
        print(f"\n📁 Full metrics saved to: artifacts/model_metrics.json")

    except Exception as e:
        print("❌ Error loading data or training model:", e)
