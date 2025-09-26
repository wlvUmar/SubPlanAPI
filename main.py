import logging
from app.db.session import sessionmanager
from logger_setup import setup_logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import user
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

if __name__ == "__main__":
	uvicorn.run(app="main:app", log_config=None, reload=True)