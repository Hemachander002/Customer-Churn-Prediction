from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import re


class PredictionPipeline:

    def __init__(self):

        self.model = joblib.load(
            Path("artifacts/model_trainer/model.joblib")
        )

        self.training_cols = joblib.load(
            Path("artifacts/model_trainer/columns.pkl")
        )

    # =====================================================
    # PREPROCESSING
    # =====================================================

    def preprocess(self, df: pd.DataFrame):
        df = df.copy()
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        df.drop("customerID", axis=1, inplace=True, errors="ignore")
        df.fillna(0, inplace=True)
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



        for col in self.training_cols:

            if col not in df.columns:
                df[col] = 0

        df = df[self.training_cols]

        return df

    def risk_category(self, prob):
        if prob >= 0.7:
            return "High Risk"
        elif prob >= 0.4:
            return "Medium Risk"

        return "Low Risk"
    
    def predict(self, df: pd.DataFrame):

        processed_data = self.preprocess(df)

        prediction = self.model.predict(processed_data)

        probability = self.model.predict_proba(processed_data)[:, 1]

        result_df = df.copy()

        result_df["prediction"] = prediction

        result_df["churn_probability"] = probability

        result_df["risk_level"] = result_df["churn_probability"].apply(lambda x: self.risk_category(x))

        result_df["prediction_label"] = result_df["prediction"].map({0: "No Churn",1: "Likely to Churn"})

        return result_df
    
    