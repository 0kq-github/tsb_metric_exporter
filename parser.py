from utils import silent_parse_nbt
from mcrcon import MCRcon
from models import Metric, User, Shard, Island, Artifact, Damage
from typing import List, Dict, Literal
from collections import defaultdict

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
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      raw_user = mcr.command("data get storage metric: User")
      raw_shard = mcr.command("data get storage metric: Shard")
      raw_island = mcr.command("data get storage metric: Island")
      raw_artifact_used = mcr.command("data get storage metric: Artifact.Used")
      raw_damage = mcr.command("data get storage metric: Damage")
    nbt_user,nbt_shard,nbt_island,nbt_artifact_used,nbt_damage = None,None,None,None,None
    if not raw_user.startswith("Found no elements"): nbt_user = silent_parse_nbt(" ".join(raw_user.split(" ",6)[6:]))
    if not raw_shard.startswith("Found no elements"): nbt_shard = silent_parse_nbt(" ".join(raw_shard.split(" ",6)[6:]))
    if not raw_island.startswith("Found no elements"): nbt_island = silent_parse_nbt(" ".join(raw_island.split(" ",6)[6:]))
    if not raw_artifact_used.startswith("Found no elements"): nbt_artifact_used = silent_parse_nbt(" ".join(raw_artifact_used.split(" ",6)[6:]))
    if not raw_damage.startswith("Found no elements"): nbt_damage = silent_parse_nbt(" ".join(raw_damage.split(" ",6)[6:]))
    self._data = Metric(User=User(**nbt_user) if nbt_user else None,Shard=Shard(**nbt_shard) if nbt_shard else None,Island=Island(**nbt_island) if nbt_island else None,Artifact=Artifact(Used=nbt_artifact_used) if nbt_artifact_used else None,Damage=Damage(**nbt_damage) if nbt_damage else None)
    return self._data

  def fetch_difficulty(self) -> int:
    """RCONで難易度を取得
    """
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      result = mcr.command("scoreboard players get $Difficulty Global")
    print(result)
    return int(result.split(" ")[-2])
  
  def fetch_entity_count(self) -> int:
    """RCONでエンティティ数を取得
    """
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      result = mcr.command("execute if entity @e")
    return int(result.split(" ")[-1])

  def fetch_bonus(self) -> List[int]:
    """RCONでステータスボーナスを取得
    """
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      bonus_health = int(mcr.command("scoreboard players get $BonusHealth Global").split(" ")[2])
      bonus_mp = int(mcr.command("scoreboard players get $BonusMP Global").split(" ")[2])
      bonus_attack = int(mcr.command("scoreboard players get $BonusAttack Global").split(" ")[2])
      bonus_defense = int(mcr.command("scoreboard players get $BonusDefense Global").split(" ")[2])
    return [bonus_health,bonus_mp,bonus_attack,bonus_defense]

  def fetch_player_count(self) -> int:
    """RCONでプレイヤー数を取得
    """
    with MCRcon(host=self.host,port=self.port,password=self.password) as mcr:
      player_list = mcr.command("list")
    return int(player_list.split(" ")[2])

  def parse_to_prometheus(self) -> str:
    from_storage = to_prometheus_metric(self._data)
    difficulty = set_metric(name="tsbmetric_difficulty",label_name="type",values={"difficulty":str(self.fetch_difficulty())},help="Difficulty of server",type="gauge")
    player_online = set_metric(name="tsbmetric_player_online",label_name="type",values={"player_online":str(self.fetch_player_count())},help="Player count of server",type="gauge")
    entity_count = set_metric(name="tsbmetric_entity_count",label_name="type",values={"entity_count":str(self.fetch_entity_count())},help="Entity count of server",type="gauge")
    bonus = set_metric(name="tsbmetric_status_bonus",label_name="type",values={"health":str(self.fetch_bonus()[0]),"mp":str(self.fetch_bonus()[1]),"attack":str(self.fetch_bonus()[2]),"defense":str(self.fetch_bonus()[3])},help="Global status bonus",type="gauge")
    return from_storage + difficulty + player_online + entity_count + bonus

def set_metric(name:str,label_name:str,values:Dict[str,str | int | float],help:str="",type:Literal["gauge","counter"]="gauge") -> str:
  _help = f"# HELP {name} {help}\n" if help else ""
  _type = f"# TYPE {name} {type}\n"
  _values = "\n".join([f"{name}{{{label_name}=\"{key}\"}} {value}" for key,value in values.items()])
  return f"\n{_help}{_type}{_values}\n"

def to_prometheus_metric(metric:Metric) -> str:
  """Prometheusの形式に変換
  """

  result = ""
  #storageのmetricから取得した値の変形
  if not metric:
    return ""
  for key in metric.model_dump().keys():
    match key:
      case "User":
        if not metric.User:
          continue
        metric_values = {item.Name:item.Joined for item in metric.User.Pair}
        result += set_metric(name="tsbmetric_player_joined_tick",label_name="player_name",values=metric_values,help="Joined tick of player",type="gauge")
        result += set_metric(name="tsbmetric_player_joined_total",label_name="type",values={"player_joined_total":str(len(metric_values))},help="Total count of player",type="counter")
      case "Shard":
        if not metric.Shard:
          continue
        metric_values = {key[-1]:value for key,value in metric.Shard.model_dump().items()}
        result += set_metric(name="tsbmetric_shard",label_name="rarity",values=metric_values,help="Shard used count",type="counter")
      case "Island":
          if not metric.Island:
            continue
          metric_values = {str(order.ID):str(order.Difficulty) for order in metric.Island.Order}
          result += set_metric(f"tsbmetric_island_order_difficulty",label_name="island_id",values=metric_values,help="Island difficulty",type="gauge")
          result += set_metric(f"tsbmetric_island_purified",label_name="type",values={"island_purified":str(len(metric_values))},help="Purified island count",type="counter")
      case "Artifact":
        if not metric.Artifact:
          continue
        used_count = defaultdict(lambda:0)
        for artifact in metric.Artifact.Used:
          used_count[artifact.ID] += 1
        result += set_metric(f"tsbmetric_artifact_used",label_name="artifact_id",values=used_count,help="Artifact use count",type="counter")
      case "Damage":
        if not metric.Damage:
          continue
        angel_values = {key:value for key,value in metric.Damage.Angel.model_dump().items()}
        normal_values = {key:value for key,value in metric.Damage.Normal.model_dump().items()}
        result += set_metric(f"tsbmetric_damage_angel",label_name="damage_type",values=angel_values,help="Angel damage count",type="counter")
        result += set_metric(f"tsbmetric_damage_normal",label_name="damage_type",values=normal_values,help="Normal damage count",type="counter")
  return result

if __name__ == "__main__":
  client = TSBMetric()
  print(client.fetch_metric())