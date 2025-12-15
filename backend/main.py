from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="Insurance Charges Prediction API")

# Load model and columns
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "insurance_xgb_model.pkl")
COLS_PATH = os.path.join(BASE_DIR, "insurance_columns.pkl")

model = joblib.load(MODEL_PATH)
columns = joblib.load(COLS_PATH)

# Input schema
class InsuranceInput(BaseModel):
    age: int
    sex: str              # Male / Female
    bmi: float
    children: int
    smoker: str           # yes / no
    region: str           # southeast / other

@app.get("/")
def root():
    return {"status": "ok", "message": "Insurance Charges API running."}

@app.post("/predict")
def predict_charges(data: InsuranceInput):
    # Encode categorical fields
    sex_numeric = 1 if data.sex.lower() == "male" else 0
    smoker_numeric = 1 if data.smoker.lower() == "yes" else 0
    region_southeast = 1 if data.region.lower() == "southeast" else 0

    # Feature engineering
    bmi_smoker_numeric = data.bmi * smoker_numeric

    bmi_category_Normal = 1 if data.bmi < 25 else 0
    bmi_category_Overweight = 1 if 25 <= data.bmi < 30 else 0
    bmi_category_Obese = 1 if data.bmi >= 30 else 0

    AgeGroup_Senior = 1 if data.age >= 45 else 0

    # Create input dataframe
    row = pd.DataFrame([{
        "age": data.age,
        "sex": sex_numeric,
        "bmi": data.bmi,
        "children": data.children,
        "smoker": smoker_numeric,
        "charges": 0,  # dummy placeholder (not used by model)
        "bmi_smoker_numeric": bmi_smoker_numeric,
        "region_southeast": region_southeast,
        "bmi_category_Normal": bmi_category_Normal,
        "bmi_category_Overweight": bmi_category_Overweight,
        "bmi_category_Obese": bmi_category_Obese,
        "AgeGroup_Senior": AgeGroup_Senior
    }])

    # ensure columns order
    row = row[columns]

    # Prediction
    prediction = float(model.predict(row)[0])

    return {
        "predicted_insurance_charges": round(prediction, 2)
    }
