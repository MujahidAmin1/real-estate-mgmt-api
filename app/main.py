from fastapi import FastAPI

app = FastAPI(title="Real Estate Management API")

@app.get("/")
def read_root():
    return {"message: Real Estate Management API is working"}
