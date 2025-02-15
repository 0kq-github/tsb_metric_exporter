from nbtlib import parse_nbt, Compound, List

def silent_parse_nbt(nbt:str) -> Compound | List:
  try:
    return parse_nbt(nbt)
  except Exception as e:
    print(e)
    return {}