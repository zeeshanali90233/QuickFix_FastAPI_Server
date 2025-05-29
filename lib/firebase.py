from config.firebase import initialize_firebase
from firebase_admin import db
import pandas as pd
from prophet import Prophet
import pickle
from datetime import datetime, timedelta
import math
import random
import os


# Initialize Firebase
initialize_firebase()

def get_dummy_data():
    """
    Generate dummy data for specific work services
    """
    services = [
        "Heating and Cooling System",
        "Electrical",
        "Plumbering",
        "Drainage",
        "Any Other Source"
    ]
    
    dummy_data = {}
    base_date = datetime.now() - timedelta(days=30)
    
    for service in services:
        dummy_data[service] = []
        for i in range(15):
            date = base_date + timedelta(days=i*2)  # Spread data over 30 days
            dummy_data[service].append({
                'ds': date.strftime("%Y-%m-%d"),
                'y': int(100 + 50 * (1 + math.sin(i / 2)) + random.randint(-10, 10))
            })
    
    return dummy_data

def train_model_daily():
    """
    Fetch data from the 'requests' collection in Firebase Realtime Database,
    group by job_type, and train models for each job type.
    """
    # Check Models Directory create if not
    if not os.path.exists("models"):
        os.makedirs("models")
    # Reference to the 'requests' collection
    ref = db.reference('request')
    
    # Fetch all data from the 'requests' collection
    all_requests = ref.get()
    
    if not all_requests:
        print("No data found in the 'requests' collection.")
        return
    
    # Group data by job_type
    job_type_data = get_dummy_data()
    for req in all_requests.values():
        job_type = req.get('requestDetail')
        if job_type not in job_type_data:
            job_type_data[job_type] = []
        dt = datetime.strptime(req.get('timeStamp'), "%m/%d/%Y, %I:%M:%S %p")
        formatted_date = dt.strftime("%Y-%m-%d")
        job_type_data[job_type].append({'ds': formatted_date, 'y': 1})

    # Train models for each job_type
    for job_type, data in job_type_data.items():
        try:
            print(f"Training model for job_type: {job_type} with {len(data)} records.")
            
            # Prepare DataFrame
            df = pd.DataFrame(data)
            df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
            df['cap'] = 1000
            df['floor'] = 0
            
            # Initialize and fit the Prophet model
            model = Prophet()
            model.fit(df)
            
            # Save the model to a file
            model_path = f"models/{job_type}_model_daily.pickle"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")
            print(f"Model for job_type '{job_type}' trained and saved at {formatted_datetime}.")
        
        except Exception as e:
            print(f"An error occurred while training model for job_type '{job_type}': {str(e)}")

def train_model_monthly():
    """
    Fetch data from the 'requests' collection in Firebase Realtime Database,
    group by job_type, and train monthly models for each job type.
    """
    # Reference to the 'requests' collection
    ref = db.reference('requests')
    
    # Fetch all data from the 'requests' collection
    all_requests = ref.get()
    
    if not all_requests:
        print("No data found in the 'requests' collection.")
        return
    
    # Group data by job_type
    job_type_data = {}
    for req in all_requests.values():
        job_type = req.get('job_type')
        if job_type not in job_type_data:
            job_type_data[job_type] = []
        job_type_data[job_type].append({'ds': req.get('date'), 'y': int(req.get('count'))})
    
    # Train models for each job_type
    for job_type, data in job_type_data.items():
        try:
            print(f"Training monthly model for job_type: {job_type} with {len(data)} records.")
            
            # Prepare DataFrame
            df = pd.DataFrame(data)
            df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
            df['cap'] = 1000
            df['floor'] = 0
            
            # Initialize and fit the Prophet model with monthly seasonality
            model = Prophet(
                growth='linear',
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                seasonality_mode='additive',
                changepoint_prior_scale=1
            )
            model.add_seasonality(name='monthly', period=28, fourier_order=1)
            model.fit(df)
            
            # Save the model to a file
            model_path = f"models/{job_type}_model_monthly.pickle"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%d-%b-%y %H:%M:%S")
            print(f"Monthly model for job_type '{job_type}' trained and saved at {formatted_datetime}.")
        
        except Exception as e:
            print(f"An error occurred while training monthly model for job_type '{job_type}': {str(e)}")
