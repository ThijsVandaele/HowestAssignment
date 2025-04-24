from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
import routes, models, database
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Adding tables if they do not exist.")
    models.Base.metadata.create_all(bind=database.engine)
    yield 
    logger.info("Finished checking tables.")

app = FastAPI(lifespan=lifespan)
app.include_router(routes.router)

@app.get("/healthz", tags=["Health"])
async def liveness_probe():
    logger.info("Healthcheck")
    return {"status": "alive"}

@app.get("/readiness", tags=["Health"])
async def readiness_probe():
    logger.info("Readiness check")
    try:
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))  
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return {"status": "unready"}