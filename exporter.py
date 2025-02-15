import json
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import os
from tsbmetric import TSBMetricRouter

load_dotenv(dotenv_path=".env",verbose=True)
app = FastAPI()

app.include_router(TSBMetricRouter().router)



if __name__ == "__main__":
  uvicorn.run(app="exporter:app",host=os.getenv("APP_HOST"),port=int(os.getenv("APP_PORT")))