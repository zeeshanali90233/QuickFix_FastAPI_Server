from fastapi import FastAPI
from controllers.v1 import main as main_v1


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Quickfix Machine Learning Server"}


app.include_router(main_v1.router,prefix="/v1")
     

        
        