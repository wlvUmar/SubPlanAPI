import logging
from app.db.session import sessionmanager
from logger_setup import setup_logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, plan, subscription, payment, invoice, admin
from config import settings
import uvicorn

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger(app.__class__.__name__)
    logger.info("Initializing Database")
    try:
        await sessionmanager.init_db()
    except Exception as e:
        logger.error(e)
    yield
    logger.info("Shutting down")

    
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(user, prefix="/user")
app.include_router(plan, prefix="/plans")
app.include_router(subscription, prefix="/subscriptions")
app.include_router(payment, prefix="/payments")
app.include_router(invoice, prefix="/invoices")
app.include_router(admin, prefix="/admin")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or []
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
	uvicorn.run(app="main:app", log_config=None, reload=True)