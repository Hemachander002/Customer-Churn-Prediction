from src.customer_churn_prediction.config.configuration import ConfigurationManager
from src.customer_churn_prediction.components.data_transformation import DataTransformation
from src.customer_churn_prediction.entity.config_entity import DataTransformationConfig
from src.customer_churn_prediction import logger
from pathlib import Path


STAGE_NAME="Data Transformation Stage"

class DataTransformationPipeline:
    def __init__(self):
        pass
    def InitializeDataTransformationPipeline(self):
        try:
            with open(Path("artifacts/data_validation/status.txt"), "r") as f:
                status = f.read().split(" ")[-1]
                status = status.strip()
            if status == "True":
                config = ConfigurationManager()
                data_transformation_config = config.get_data_transformation_config()
                data_transform = DataTransformation(config=data_transformation_config)
                transformed_data = data_transform.transform_data()
                data_transform.split_data(transformed_data)
        except Exception as e:
            logger.exception(e)
            raise e

if __name__ == "__main__":
    try:
        logger.info("Starting data transformation pipeline...")
        data_transformation_pipeline = DataTransformationPipeline()
        data_transformation_pipeline.InitializeDataTransformationPipeline()
        logger.info("Data transformation pipeline completed successfully!")
    except Exception as e:
        logger.exception(e)
        raise e