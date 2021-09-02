"""
Serve PyCaret prediction pipeline using FastAPI.
"""
import pandas as pd
from pycaret.regression import load_model, predict_model
from fastapi import FastAPI
import uvicorn

app = FastAPI()

model = load_model("diamond-pipeline")


@app.post("/predict")
def predict(
    carat_weight: float,
    cut: str,
    color: str,
    clarity: str,
    polish: str,
    symmetry: str,
    report: str,
):
    data = pd.DataFrame([[carat_weight, cut, color, clarity, polish, symmetry, report]])
    data.columns = [
        "Carat Weight",
        "Cut",
        "Color",
        "Clarity",
        "Polish",
        "Symmetry",
        "Report",
    ]

    predictions = predict_model(model, data=data)
    return {"prediction": int(predictions["Label"][0])}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
