from fastapi import APIRouter
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA,ARIMAResults
from datetime import datetime
from classes.train_predict import PredictionRequest

router = APIRouter()


@router.post("/requests")
async def predict(payload: PredictionRequest):
    stepsToPredict=payload.stepsToPredict
    precictionStartDate=payload.precictionStartDate
    try:
        model_fit = ARIMAResults.load("arima_requests_model_v1.pickle")
        # Forecast the next 
        forecast = model_fit.forecast(steps=stepsToPredict)
        # Convert forecast to a list of dictionaries
        forecast_list = forecast.to_list()
        
        current_datetime = datetime.strptime(precictionStartDate, "%Y-%m-%d")
        forecast_dates = pd.date_range(start=current_datetime, periods=stepsToPredict, freq='D').to_list()

        forecast_data = [{'date': date.strftime('%Y-%m-%d'), 'forecast': value} for date, value in zip(forecast_dates, forecast_list)]

        return {"message": "Forecast generated successfully", "forecast": forecast_data}
    except Exception as e:
        return {"message": f"An Error Occurred: {str(e)}", "forecast": []}
  
  
  