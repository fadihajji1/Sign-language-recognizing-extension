from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from inference import load_inference_bundle
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.bundle = load_inference_bundle()
        app.state.model_error = None
    except Exception as exc:
        app.state.bundle = None
        app.state.model_error = str(exc)
    yield


app = FastAPI(
    title="TSL Recognition API",
    description="Isolated Tunisian Sign Language image recognition.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router)
