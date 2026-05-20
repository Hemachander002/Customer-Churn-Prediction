#from src.customer_churn_prediction.pipeline.model_evaluation_pipeline import ModelEvaluationPipeline
#from src.laptop_price_prediction.pipeline.model_training_pipeline import ModelTrainerPipeline
from src.customer_churn_prediction.pipeline.model_training_pipeline import ModelTrainerPipeline
from src.customer_churn_prediction.pipeline.data_validation_pipeline import DataValidationPipeline
from src.customer_churn_prediction import logger
from src.customer_churn_prediction.pipeline.data_ingestion_pipeline import DataIngestionTrainingPipeline
from src.customer_churn_prediction.pipeline.data_transformation_pipeline import DataTransformationPipeline

STAGE_NAME="Data Ingestion Stage"
try:
    logger.info(f">>>>>>> stage {STAGE_NAME} started <<<<<<<")
    obj=DataIngestionTrainingPipeline()
    obj.InitiateDataIngestionTrainingPipeline()
    logger.info(f">>>>>>> stage {STAGE_NAME} completed <<<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e

STAGE_NAME="Data Validation Stage"
try:
    logger.info(f">>>>>>> stage {STAGE_NAME} started <<<<<<<")
    obj=DataValidationPipeline()
    obj.InitiateDataValidation()
    logger.info(f">>>>>>> stage {STAGE_NAME} completed <<<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e

STAGE_NAME="Data Transformation Stage"
try:
    logger.info(f">>>>>>> stage {STAGE_NAME} started <<<<<<<")
    obj=DataTransformationPipeline()
    obj.InitializeDataTransformationPipeline()
    logger.info(f">>>>>>> stage {STAGE_NAME} completed <<<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e

STAGE_NAME="Model Trainer Stage"
try:
    logger.info(f">>>>>>> stage {STAGE_NAME} started <<<<<<<")
    obj=ModelTrainerPipeline()
    obj.InitiateModelTrainerPipeline()
    logger.info(f">>>>>>> stage {STAGE_NAME} completed <<<<<<<\n\nx==========x")
except Exception as e:
    logger.exception(e)
    raise e