from pydantic import BaseModel



class RequestItem(BaseModel):
    date: str
    count: int
class RequestModel(BaseModel):
    name: str
    data: list[RequestItem]

class RequestsArray(BaseModel):
    requests: list[RequestModel]
    
class PredictionRequest(BaseModel):
    stepsToPredict:int=5
    predictionStartDate:str
    job_type:str
    frequency:str
    
class TrainRequestsModel(BaseModel):
    requests:RequestsArray