from fastapi import APIRouter
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from classes.train_predict import TrainRequestsModel
from prophet import Prophet
import pickle

router = APIRouter()

@router.post("/requests/daily/model")
async def train(payload: TrainRequestsModel):
    requests=payload.requests
    try:
        data = [{'ds': req.date, 'y': int(req.count)} for req in requests.requests]
        df = pd.DataFrame(data)
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

        df['cap']=1000
        df['floor']=0
        
        # Initialize and fit the Prophet model to the data
        model = Prophet()
        model.fit(df)
        with open(f"models/daily.pickle", 'wb') as f:
            pickle.dump(model, f)

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")

        return {"message":f"Requests Train at {formatted_datetime}"}
    except Exception as e:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")
        return {"message": f"An Error Occurred: {str(e)}","datetime":formatted_datetime}
  
  
@router.post("/requests/monthly/model")
async def train(payload: TrainRequestsModel):
    requests=payload.requests
    try:
        data = [{'ds': req.date, 'y': int(req.count)} for req in requests.requests]
        df = pd.DataFrame(data)
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

        df['cap']=1000
        df['floor']=0
        
        model = Prophet(
                growth='linear',            # Linear growth, you can try logistic if there's a cap
                yearly_seasonality=False,     # Include yearly seasonality
                weekly_seasonality=False,    # We don't need weekly seasonality for monthly data
                daily_seasonality=False,     # No daily seasonality needed
                seasonality_mode='additive', # Additive model, can try 'multiplicative' if needed
                changepoint_prior_scale=1, # Adjust to control flexibility in trend changes
            )
        
        model.add_seasonality(name='monthly', period=28, fourier_order=1)
        model.fit(df)
        with open(f"models/monthly.pickle", 'wb') as f:
            pickle.dump(model, f)

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")

        return {"message":f"Requests Train at {formatted_datetime}"}
    except Exception as e:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")
        return {"message": f"An Error Occurred: {str(e)}","datetime":formatted_datetime}
  
  
  