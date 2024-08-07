from fastapi import APIRouter
from routers.v1.requests import train,predict

router=APIRouter()



router.include_router(train.router,prefix="/train")
router.include_router(predict.router,prefix="/predict")
