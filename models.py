from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PairItem(BaseModel):
    ID: int
    Joined: int
    Name: str


class User(BaseModel):
    Pair: List[PairItem]


class Shard(BaseModel):
    rarity_1: Optional[int] = Field(0, alias='1')
    rarity_2: Optional[int] = Field(0, alias='2')
    rarity_3: Optional[int] = Field(0, alias='3')
    rarity_4: Optional[int] = Field(0, alias='4')


class OrderItem(BaseModel):
    Difficulty: int
    Time: int
    ID: int


class Island(BaseModel):
    Order: List[OrderItem]


class UsedItem(BaseModel):
    Time: int
    ID: int


class Artifact(BaseModel):
    Used: List[UsedItem]


class DamageAngel(BaseModel):
    Bypass: Optional[int] = 0
    Weak: Optional[int] = 0
    Resist: Optional[int] = 0
    Normal: Optional[int] = 0


class DamageNormal(BaseModel):
    Bypass: Optional[int] = 0
    Weak: Optional[int] = 0
    Resist: Optional[int] = 0
    Normal: Optional[int] = 0


class Damage(BaseModel):
    Angel: DamageAngel
    Normal: DamageNormal


class Metric(BaseModel,extra='allow'):
    User: User | None
    Shard: Shard | None
    Island: Island | None
    Artifact: Artifact | None
    Damage: Damage | None
