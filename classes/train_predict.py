from pydantic import BaseModel



class RequestItem(BaseModel):
    date: str
    count: int

class RequestsArray(BaseModel):
    requests: list[RequestItem]
    
class PredictionRequest(BaseModel):
    stepsToPredict:int=5
    precictionStartDate:str
    
class TrainRequestsModel(BaseModel):
    requests:RequestsArray