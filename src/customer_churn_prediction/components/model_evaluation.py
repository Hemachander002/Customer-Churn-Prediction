import os
import joblib
import dagshub
import mlflow
from mlflow.metrics import mae
import mlflow.sklearn
from sklearn.metrics import f1_score,recall_score
from urllib.parse import urlparse
from src.customer_churn_prediction.entity.config_entity import ModelEvaluationConfig
from src.customer_churn_prediction.utils.common import save_json
from src.customer_churn_prediction.config.configuration import ConfigurationManager, ModelEvaluationConfig
from pathlib import Path
import numpy as np
import pandas as pd


os.environ["MLFLOW_TRACKING_URI"] = "https://dagshub.com/Hemachander002/Customer-Churn-Prediction.mlflow"
os.environ["MLFLOW_TRACKING_USERNAME"] = "Hemachander002"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "254edea09d48445e8e8de0075ef293dfc5f9e30a"


class ModelEvaluator:
    def __init__(self,config: ModelEvaluationConfig):
        self.config = config
        self.model_path = config.model_path
        self.X_test = config.test_data_path
        self.y_test = config.target_column
        self.registry_uri = config.mlflow_uri
        self.metric_file_name = config.metric_file_name

    def eval_metrics(self,actual, predicted):
        f1 = f1_score(actual, predicted)
        recall= recall_score(actual, predicted)

        return f1, recall

    def log_into_mlflow(self):
        test_data = pd.read_csv(self.X_test)
        y_test = test_data[self.y_test]
        X_test = test_data.drop(columns=[self.y_test])
        mlflow.set_registry_uri(self.registry_uri)
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
        model = joblib.load(self.model_path)

        with mlflow.start_run():
            predicted = model.predict(X_test)
            f1, recall = self.eval_metrics(y_test, predicted)
            scores = {"f1": f1, "recall": recall}
            save_json(path= Path(self.metric_file_name), data=scores)
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(scores)

            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(model, name =  "model", registered_model_name="Best_Model")
            else:
                mlflow.sklearn.log_model(model, name =  "model")


if __name__ == "__main__":
    try:
        config = ConfigurationManager()
        model_eval_config = config.get_model_evaluation_config()
        model_eval = ModelEvaluator(config=model_eval_config)
        model_eval.log_into_mlflow()
    except Exception as e:
        raise e