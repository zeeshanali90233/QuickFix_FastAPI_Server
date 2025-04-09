from fastapi import FastAPI
from controllers.v1 import main as main_v1
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from contextlib import asynccontextmanager
from apscheduler.triggers.cron import CronTrigger
from lib.firebase import train_model_daily,train_model_monthly

app = FastAPI()

scheduler = AsyncIOScheduler(timezone=utc)
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

@app.get("/")
async def root():
    train_model_daily()
    return {"message": "Welcome to Quickfix Machine Learning Server"}


app.include_router(main_v1.router,prefix="/v1")
     
# Daily
trigger= CronTrigger(day_of_week="mon-sun", hour=19,minute=5)
scheduler.add_job(train_model_daily,trigger)
# Monthly
trigger= CronTrigger(month="jan-dec", day=2,hour=2,minute=10)
scheduler.add_job(train_model_monthly,trigger)
        
        