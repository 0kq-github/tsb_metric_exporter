from nbtlib import parse_nbt
from mcrcon import MCRcon
from models import Metric, User, Shard, Island, Artifact
from typing import List, Dict, Literal

class TSBMetric:
  def __init__(self,host:str="localhost",port:int=25575,password:str="") -> None:
    self.host = host
    self.port = port
    self.password = password
    self._data:Metric = None
  
  def to_json(self,*args,**kwargs) -> str:
    return self._data.model_dump_json(*args,**kwargs)

  def get_user(self) -> User:
    return self._data.User
  
  def get_shard(self) -> Shard:
    return self._data.Shard

  def get_island(self) -> Island:
    return self._data.Island

  def get_artifact(self) -> Artifact:
    return self._data.Artifact

  def get_metric(self) -> Metric:
    return self._data

  def fetch_metric(self) -> Metric:
    """RCONでメトリクスを取得
    """
    print(f"{self.host=},{self.port=},{self.password=}")
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      result = mcr.command("data get storage metric:")
    nbt:dict = parse_nbt(result[44:])
    if not nbt.get("User"): nbt["User"] = None
    if not nbt.get("Shard"): nbt["Shard"] = None
    if not nbt.get("Shard").get("1"): nbt["Shard"]["1"] = 0
    if not nbt.get("Shard").get("2"): nbt["Shard"]["2"] = 0
    if not nbt.get("Shard").get("3"): nbt["Shard"]["3"] = 0
    if not nbt.get("Shard").get("4"): nbt["Shard"]["4"] = 0
    if not nbt.get("Island"): nbt["Island"] = None
    if not nbt.get("Artifact"): nbt["Artifact"] = None
    self._data = Metric(**nbt)
    return self._data

def to_prometheus_metric(metric:Metric) -> str:
  """Prometheusの形式に変換
  """

  def _to_prometheus_metric(name:str,label_name:str,values:Dict[str,str],help:str="",type:Literal["gauge","counter"]="gauge") -> str:
    _help = f"# HELP {name} {help}\n" if help else ""
    _type = f"# TYPE {name} {type}\n"
    _values = "\n".join([f"{name}{{{label_name}=\"{key}\"}} {value}" for key,value in values.items()])
    return f"\n{_help}{_type}{_values}\n"

  result = ""
  for key in metric.model_dump().keys():
    match key:
      case "User":
        if not metric.User:
          continue
        metric_values = {item.Name:item.Joined for item in metric.User.Pair}
        result += _to_prometheus_metric(name="tsbmetric_player_joined_tick",label_name="player_name",values=metric_values,help="Joined tick of player",type="gauge")
        result += _to_prometheus_metric(name="tsbmetric_player_joined_total",label_name="player",values={"player":str(len(metric_values))},help="Total count of player",type="counter")
      case "Shard":
        if not metric.Shard:
          continue
        metric_values = {key[-1]:value for key,value in metric.Shard.model_dump().items()}
        result += _to_prometheus_metric(name="tsbmetric_shard",label_name="rarity",values=metric_values,help="Shard used count",type="counter")
      case "Island":
          if not metric.Island:
            continue
          metric_values = {str(order.ID):str(order.Difficulty) for order in metric.Island.Order}
          result += _to_prometheus_metric(f"tsbmetric_island_order_difficulty",label_name="island_id",values=metric_values,help="Island difficulty",type="gauge")
          result += _to_prometheus_metric(f"tsbmetric_island_purified",label_name="count",values={"count":str(len(metric_values))},help="Purified island count",type="counter")
      case "Artifact":
        if not metric.Artifact:
          continue
        metric_values = {str(used.ID):str(used.Time) for used in metric.Artifact.Used}
        result += _to_prometheus_metric(f"tsbmetric_artifact_used_time",label_name="artifact_id",values=metric_values,help="Artifact used time",type="gauge")
  return result

if __name__ == "__main__":
  client = TSBMetric()
  print(client.fetch_metric())