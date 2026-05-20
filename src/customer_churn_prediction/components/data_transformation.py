import os
import re
from src.customer_churn_prediction import logger
from src.customer_churn_prediction.entity.config_entity import (DataTransformationConfig)
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

class DataTransformation:
    def __init__(self,config:DataTransformationConfig):
        self.config=config
    
    def transform_data(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.config.data_path)
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
            df.drop("customerID", axis=1, inplace=True)
            df["Churn"] = df["Churn"].apply(lambda x : 1 if x == "Yes" else 0)
            df.dropna(inplace=True)
            df["gender"] = df["gender"].apply(lambda x : 1 if x == "Male" else 0)
            li = ["Partner" , "Dependents" , "PhoneService" , "PaperlessBilling"]
            for col in li:
                df[col] = df[col].map({"Yes": 1, "No": 0})
            df["avg_charge"] = df["TotalCharges"] / (df["tenure"] + 1)
            df["tenure_group"] = (df["tenure"] < 12).astype(int)
            df["high_value_customer"] = (df["MonthlyCharges"] > df["MonthlyCharges"].median()).astype(int)
            df = pd.get_dummies(df, drop_first=True)
            df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_"))
            bool_cols = df.select_dtypes(include="bool").columns
            df[bool_cols] = df[bool_cols].astype(int)

            return df
        except Exception as e:
            logger.exception(e)
            raise e
        
    def split_data(self,df:pd.DataFrame):
        train,test = train_test_split(df, test_size=0.2, random_state=42)
        train.to_csv(os.path.join(self.config.root_dir,"train.csv"), index = False)
        test.to_csv(os.path.join(self.config.root_dir,"test.csv"), index = False)
        logger.info("Data split successful!")