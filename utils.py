from nbtlib import parse_nbt

def silent_parse_nbt(nbt:str) -> dict:
  try:
    return parse_nbt(nbt)
  except Exception as e:
    print(e)
    return {}