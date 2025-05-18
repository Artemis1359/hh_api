from fastapi import FastAPI
from app.db import init_models
from app.routers.candidates import candidates_router

app = FastAPI(
    title="HH_API_Service",
    description="Сервис для работы с Headhunter API",
    root_path="/hh/v1",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)

app.include_router(candidates_router)

if __name__ == "__main__":
    import asyncio

    asyncio.run(init_models())
