from fastapi import FastAPI
from app.database import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real Estate Management API")

@app.get("/")
def read_root():
    return {"message: Real Estate Management API is working"}
