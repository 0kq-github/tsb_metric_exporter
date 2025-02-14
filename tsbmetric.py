from fastapi import Response
from fastapi.routing import APIRouter
from fastapi_restful.cbv import cbv
from parser import TSBMetric, to_prometheus_metric
import os

router = APIRouter()

@cbv(router)
class TSBMetricRouter:
  def __init__(self) -> None:
    self.client = TSBMetric(host=os.getenv("RCON_HOST"),port=int(os.getenv("RCON_PORT")),password=os.getenv("RCON_PASSWORD"))
    self.router = router

  @router.get("/metrics")
  async def get_metrics(self) -> Response:
    try:
      self.client.fetch_metric()
    except ConnectionError as e:
      return Response(content=f"RCON Connection Error\n{e}",status_code=503)
    return Response(content=self.client.parse_to_prometheus())
