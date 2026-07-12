from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from app.core.apscheduler import delete_expired_tokens
from app.db.database import engine, Base
from app.modules.admin import router as admin_router
from app.modules.payments import payment_router
from app.modules.profile import router as profile_router
from app.modules.users import router as auth_router
from app.modules.properties import router as properties_router
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.exceptions import (
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    ConflictException,
    BadRequestException
)


Base.metadata.create_all(bind=engine)
scheduler: BackgroundScheduler = BackgroundScheduler()

app = FastAPI(title="Real Estate Management API")
app.openapi_version = "3.0.3"

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(properties_router)
app.include_router(payment_router.router)


def use_swagger_file_upload_schema(value: Any) -> None:
    if isinstance(value, dict):
        if value.get("contentMediaType") == "application/octet-stream":
            value.pop("contentMediaType", None)
            value["format"] = "binary"

        for child in value.values():
            use_swagger_file_upload_schema(child)
    elif isinstance(value, list):
        for child in value:
            use_swagger_file_upload_schema(child)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        openapi_version=app.openapi_version,
    )
    use_swagger_file_upload_schema(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/")
def read_root():
    return {"message": "Real Estate Management API is working"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    delete_expired_tokens()
    scheduler.start()
    
    yield  # app is running
    
    # shutdown
    scheduler.shutdown()


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"detail": exc.detail})

@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(status_code=403, content={"detail": exc.detail})

@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(status_code=401, content={"detail": exc.detail})

@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"detail": exc.detail})

@app.exception_handler(BadRequestException)
async def bad_request_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=400, content={"detail": exc.detail})

# handles Pydantic validation errors (wrong types, missing fields)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(l) for l in error["loc"][1:]),
            "message": error["msg"]
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})

# catch-all for any unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
