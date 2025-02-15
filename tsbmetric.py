from fastapi import Response
from fastapi.routing import APIRouter
from parser import TSBMetric
import os

router = APIRouter()
client = TSBMetric(host=os.getenv("RCON_HOST"),port=int(os.getenv("RCON_PORT")),password=os.getenv("RCON_PASSWORD"))

@router.get("/metrics",tags=["exporter"])
async def get_metrics() -> Response:
  try:
    client.fetch_metric()
  except ConnectionError as e:
    return Response(content=f"RCON Connection Error\n{e}",status_code=503)
  return Response(content=client.parse_to_prometheus())
