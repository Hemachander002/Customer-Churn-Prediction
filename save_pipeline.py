from src.customer_churn_prediction.pipeline.preprocessing_pipeline import PredictionPipeline
import joblib
from pathlib import Path

pipeline = PredictionPipeline()

joblib.dump(
    pipeline,
    Path(
        "artifacts/model_trainer/preprocessing_pipeline.joblib"
    )
)