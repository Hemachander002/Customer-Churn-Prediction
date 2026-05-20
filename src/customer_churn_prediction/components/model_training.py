from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import os
from src.customer_churn_prediction.config.configuration import ConfigurationManager
from src.customer_churn_prediction.entity.config_entity import ModelTrainerConfig
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix,f1_score, recall_score
from src.customer_churn_prediction.utils.common import save_json
import os
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import random
from scipy.stats import uniform, randint
import pandas as pd
from src.customer_churn_prediction import logger
import joblib

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train_model(self):
        # Load the training data
        train_data = pd.read_csv(self.config.train_data_path)
        test_data = pd.read_csv(self.config.test_data_path)

        # Separate features and target variable
        X_train = train_data.drop(columns=[self.config.target_column])
        y_train = train_data[self.config.target_column]

        X_test = test_data.drop(columns=[self.config.target_column])
        y_test = test_data[self.config.target_column]


        model_params = {
            "Logistic Regression": {
                        "model": Pipeline([("scaler", StandardScaler()),("lr", LogisticRegression(max_iter=2000))]),
            "params": {
            "lr__C": [0.01, 0.1, 1, 10],
            "lr__class_weight": [None, "balanced"]
        }},

            "Random Forest": {
                        "model": RandomForestClassifier(),
            "params": {
            "n_estimators": randint(100, 400),
            "max_depth": [5, 8, 10, 12, None],
            "min_samples_leaf": [1, 2, 4],
            "class_weight": [{0:1, 1:2}, {0:1, 1:3}, "balanced"]
        }
    },

            "XGBoost": {
                "model": XGBClassifier(eval_metric="logloss"),
                "params": {
            "n_estimators": randint(100, 400),
            "max_depth": randint(3, 8),
            "learning_rate": uniform(0.01, 0.1),
            "subsample": uniform(0.7, 0.3),
            "colsample_bytree": uniform(0.7, 0.3),
            "scale_pos_weight": [1, 2, 3, 5]
        }
    }
}


        results = []
        best_models = {}
        best_model_final = None
        best_model_name = None
        best_f1_score = 0.0

        for name, mp in model_params.items():

            logger.info(f"Running RandomizedSearchCV for {name}")

            search = RandomizedSearchCV(
                estimator=mp["model"],
                param_distributions=mp["params"],
                n_iter=30,
                cv=3,

                scoring={
                    "f1": "f1",
                    "recall": "recall"
                },

                refit="f1",

                n_jobs=-1,
                random_state=42,
                verbose=1
            )

            # Train Search
            search.fit(X_train, y_train)

            # Best Model
            best_model = search.best_estimator_

            # Predictions
            y_pred = best_model.predict(X_test)

            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)

            # Save Results
            results.append({
                "Model": name,
                "Accuracy": accuracy,
                "F1 Score": f1,
                "Recall": recall
            })

            # Logging
            logger.info(f"{name} Accuracy: {accuracy}")
            logger.info(f"{name} F1 Score: {f1}")
            logger.info(f"{name} Recall: {recall}")

            # Track Best Model
            if f1 > best_f1_score:
                best_f1_score = f1
                best_model_final = best_model
                best_model_name = name

        logger.info("Saving the trained model...")
        joblib.dump(best_model_final, os.path.join(self.config.root_dir, self.config.model_name))

        return best_model_final
