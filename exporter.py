from dotenv import load_dotenv
load_dotenv(dotenv_path=".env",verbose=True)

import json
from fastapi import FastAPI
import uvicorn
import os
import tsbmetric


app = FastAPI(
  title="TSB Exporter",
  description="TSB Exporter",
  )

app.include_router(tsbmetric.router)



if __name__ == "__main__":
  uvicorn.run(app=app,host=os.getenv("APP_HOST"),port=int(os.getenv("APP_PORT")))