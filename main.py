
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
import pandas as pd
import joblib

app = FastAPI(title="Mental Health Score Prediction API")

# Load trained Random Forest pipeline
rf_best_pipeline = joblib.load("Mental_Health_Model.pkl")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "FastAPI is running"
    }


# Pydantic input validation
class StudentData(BaseModel):

    Age: int = Field(..., ge=20, lt=24)

    Gender: Literal["Male", "Female"]

    Country: str

    Academic_Level: Literal[
        "High School", "Undergraduate", "Graduate"
    ]

    Most_Used_Platform: Literal[
        "Facebook", "LinkedIn", "Instagram", "Snapchat",
        "Twitter", "YouTube", "TikTok", "LINE",
        "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"
    ]

    Purpose_Of_Use: Literal[
        "Networking", "Education", "Entertainment", "News"
    ]

    Avg_Daily_Usage_Hours: float = Field(..., ge=0, le=8.8)

    Daily_Unlocks: int = Field(..., ge=0)

    Study_Hours: float = Field(..., ge=0, le=24)

    Physical_Activity_Hours: float = Field(..., ge=0, le=24)

    Sleep_Hours_Per_Night: float = Field(..., ge=0, le=24)

    Stress_Level: Literal[
        "Low", "Medium", "High", "Very High"
    ]


# Countries retained during data preprocessing
top_countries = {
    'India', 'USA', 'Canada', 'Australia', 'UK',
    'Germany', 'Mexico', 'Turkey', 'France'
}


# Prediction response model
class PredictionResponse(BaseModel):
    Predicted_Mental_Health_Score: float


# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
def predict(data: StudentData):

    # 1. Group countries
    country_group = (
        data.Country
        if data.Country in top_countries
        else "Other"
    )

    # 2. Create input DataFrame
    input_row = pd.DataFrame([
        {
            'Age': data.Age,
            'Gender': data.Gender,
            'Country': data.Country,
            'Academic_Level': data.Academic_Level,
            'Most_Used_Platform': data.Most_Used_Platform,
            'Purpose_Of_Use': data.Purpose_Of_Use,
            'Avg_Daily_Usage_Hours': data.Avg_Daily_Usage_Hours,
            'Daily_Unlocks': data.Daily_Unlocks,
            'Study_Hours': data.Study_Hours,
            'Physical_Activity_Hours': data.Physical_Activity_Hours,
            'Sleep_Hours_Per_Night': data.Sleep_Hours_Per_Night,
            'Stress_Level': data.Stress_Level,
            'Grouped_country': country_group
        }
    ])

    # 3. Display input DataFrame
    print(input_row)

    # 4. Make prediction
    prediction = rf_best_pipeline.predict(input_row)[0]

    # 5. Return predicted Mental Health Score
    return PredictionResponse(
        Predicted_Mental_Health_Score=round(float(prediction), 2)
    )


# Lets you start the server with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
