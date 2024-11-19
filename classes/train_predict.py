from pydantic import BaseModel



class RequestItem(BaseModel):
    date: str
    count: int

class RequestsArray(BaseModel):
    requests: list[RequestItem]
    
class PredictionRequest(BaseModel):
    stepsToPredict:int=5
    predictionStartDate:str
    frequency:str
    
class TrainRequestsModel(BaseModel):
    requests:RequestsArray