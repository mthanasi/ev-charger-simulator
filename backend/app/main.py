from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.session import engine, init_models
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


def main() -> None:
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)


if __name__ == "__main__":
    main()
