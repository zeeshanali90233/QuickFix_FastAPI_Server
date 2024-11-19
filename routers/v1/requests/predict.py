from fastapi import APIRouter
import pandas as pd
from datetime import datetime
from classes.train_predict import PredictionRequest
import pickle
from prophet import Prophet
from utils.math import floor

router = APIRouter()


@router.post("/requests")
async def predict(payload: PredictionRequest):
    stepsToPredict=payload.stepsToPredict
    predictionStartDate = payload.predictionStartDate 
    frequency=payload.frequency
    
    try:
        with open(f"models/daily.pickle","rb") as f:
            model_fit=pickle.load(f)
                 
        # Create future dates for prediction
        future = model_fit.make_future_dataframe(periods=stepsToPredict)
        future['cap']=10000
        future['floor']=0
        
        print(future)
        # Forecast the future values
        forecast = model_fit.predict(future)  # Changed from forecast.predict(forecast) to model_fit.predict(future)
            
        # Get the forecast values for the specified periods
        forecast_values = forecast['yhat'].tail(stepsToPredict).values
        forecast_values=map(floor,forecast_values)
        current_datetime = datetime.strptime(predictionStartDate, "%Y-%m-%d")
        forecast_dates = pd.date_range(start=current_datetime, periods=stepsToPredict, freq='D').to_list()

        if(frequency=="monthly"):    
            # Convert start date to datetime
            current_datetime = datetime.strptime(predictionStartDate, "%Y-%m")
                
            # Create forecast dates
            forecast_dates = pd.date_range(start=current_datetime, periods=stepsToPredict, freq='M').to_list()
                
            # Create forecast data
            forecast_data = [{'month': date.strftime('%Y-%b'), 'forecast': value} 
                                for date, value in zip(forecast_dates, forecast_values)]
        else:
            # Convert start date to datetime
            current_datetime = datetime.strptime(predictionStartDate, "%Y-%m-%d")
                
            # Create forecast dates
            forecast_dates = pd.date_range(start=current_datetime, periods=stepsToPredict, freq='D').to_list()
                
            # Create forecast data
            forecast_data = [{'date': date.strftime('%Y-%m-%d'), 'forecast': value} 
                                for date, value in zip(forecast_dates, forecast_values)]
                
        return {"message": "Forecast generated successfully", "forecast": forecast_data}
    except Exception as e:
        return {"message": f"An Error Occurred: {str(e)}", "forecast": []}
  
  
  