from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.apscheduler import delete_expired_tokens
from app.db.database import engine, Base
from app.modules.users import auth_router
from app.modules.properties import property_routes
from apscheduler.schedulers.background import BackgroundScheduler
import os
from app.utils.exceptions import (
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    ConflictException,
    BadRequestException
)


uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)

Base.metadata.create_all(bind=engine)
scheduler: BackgroundScheduler = BackgroundScheduler()

app = FastAPI(title="Real Estate Management API")

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth_router.router)
app.include_router(property_routes.router)

@app.get("/")
def read_root():
    return {"message: Real Estate Management API is working"}

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