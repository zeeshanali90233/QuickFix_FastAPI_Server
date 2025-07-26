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
    Generate realistic dummy data for specific work services
    """
    services = [
        "Heating and Cooling System",
        "Electrical",
        "Plumbering",
        "Drainage",
        "Any Other Source"
    ]
    
    dummy_data = {}
    base_date = datetime.now() - timedelta(days=90)  # 3 months of data
    
    for service in services:
        dummy_data[service] = []
        
        # Generate data for each day
        for day in range(90):
            current_date = base_date + timedelta(days=day)
            
            # Base requests per day (2-3 average)
            base_requests = 2.5
            
            # Add weekly seasonality (more requests on weekdays)
            weekday_factor = 1.3 if current_date.weekday() < 5 else 0.7
            
            # Add seasonal variation (some services more popular in certain months)
            month = current_date.month
            if service == "Heating and Cooling System":
                # More requests in summer (AC) and winter (heating)
                seasonal_factor = 1.5 if month in [6, 7, 8, 12, 1, 2] else 0.8
            elif service == "Electrical":
                # Slightly higher in winter (lighting issues)
                seasonal_factor = 1.2 if month in [11, 12, 1, 2] else 0.9
            elif service == "Plumbing":
                # More in winter (frozen pipes) and spring (maintenance)
                seasonal_factor = 1.3 if month in [12, 1, 2, 3, 4] else 0.8
            elif service == "Drainage":
                # More during rainy seasons
                seasonal_factor = 1.4 if month in [3, 4, 5, 9, 10] else 0.7
            else:
                seasonal_factor = 1.0
            
            # Calculate daily requests with some randomness
            daily_requests = max(0, int(
                base_requests * weekday_factor * seasonal_factor + 
                random.gauss(0, 0.8)  # Add normal distribution noise
            ))
            
            # Ensure at least some variation (0-6 requests per day)
            daily_requests = max(0, min(6, daily_requests))
            
            # Add the data point for this day
            if daily_requests > 0:
                dummy_data[service].append({
                    'ds': current_date.strftime("%Y-%m-%d"),
                    'y': daily_requests
                })
    
    return dummy_data

def train_model_daily():
    """
    Fetch data from the 'requests' collection in Firebase Realtime Database,
    group by job_type, and train models for each job type.
    """
    print("Training daily models...")
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
    # job_type_data = {}
    
    # Real Data 
    # for req in all_requests.values():
    #     job_type = req.get('requestDetail')
    #     if job_type not in job_type_data:
    #         job_type_data[job_type] = []
    #     ts = req.get('timeStamp')
    #     try:
    #         dt = datetime.strptime(ts, "%m/%d/%Y, %I:%M:%S %p")
    #     except ValueError:
    #         dt = datetime.strptime(ts, "%d/%m/%Y, %H:%M:%S")
    #     formatted_date = dt.strftime("%Y-%m-%d")
    #     job_type_data[job_type].append({'ds': formatted_date, 'y': 1})

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
