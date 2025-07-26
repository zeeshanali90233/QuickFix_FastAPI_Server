from fastapi import FastAPI
from controllers.v1 import main as main_v1
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from contextlib import asynccontextmanager
from apscheduler.triggers.cron import CronTrigger
from lib.firebase import train_model_daily,train_model_monthly
from fastapi.middleware.cors import CORSMiddleware


scheduler = AsyncIOScheduler(timezone=utc)
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    train_model_daily()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for all add *
    allow_credentials=True,
    allow_methods=["GET", "POST","DELETE"],  # Specify allowed methods
    allow_headers=["*"],  # Specify allowed headers (e.g., "Content-Type")
)

@app.get("/")
async def root():
    return {"message": "Welcome to Quickfix Machine Learning Server"}


app.include_router(main_v1.router,prefix="/v1")
     
# Daily
trigger= CronTrigger(day_of_week="mon-sun", hour=19,minute=5)
scheduler.add_job(train_model_daily,trigger)
# Monthly
trigger= CronTrigger(month="jan-dec", day=2,hour=2,minute=10)
scheduler.add_job(train_model_monthly,trigger)
            
        