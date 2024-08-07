from fastapi import APIRouter
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from classes.train_predict import TrainRequestsModel

router = APIRouter()


  
  

@router.post("/requests/model")
async def train(payload: TrainRequestsModel):
    requests=payload.requests
    try:
        
        data = [{'date': req.date, 'count': req.count} for req in requests.requests]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])

        # Handle duplicate dates by aggregating counts
        df = df.groupby('date').sum()

        # Ensure the DataFrame index has a daily frequency
        df = df.asfreq('D', fill_value=0)

        # Fit the ARIMA model
        model = ARIMA(df['count'], order=(len(data)-1, 1, 3))  
        print(df.index[-1])
        model_fit = model.fit()
        model_fit.save("arima_requests_model_v1.pickle")

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")

        return {"message": "Requests Forcasting Model Successfully Trained", "datetime":formatted_datetime}
    except Exception as e:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")
        return {"message": f"An Error Occurred: {str(e)}","datetime":formatted_datetime}
  
  
  