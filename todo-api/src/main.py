from contextlib import asynccontextmanager
from fastapi import FastAPI
import routes, models, database

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Add tables if non exists")
    models.Base.metadata.create_all(bind=database.engine)
    yield  # Must yield control for FastAPI to run

app = FastAPI(lifespan=lifespan)
app.include_router(routes.router)
