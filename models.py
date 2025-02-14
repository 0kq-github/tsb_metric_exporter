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
    rarity_1: int = Field(..., alias='1')
    rarity_2: int = Field(..., alias='2')
    rarity_3: int = Field(..., alias='3')
    rarity_4: int = Field(..., alias='4')


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


class Metric(BaseModel,extra='allow'):
    User: User | None
    Shard: Shard | None
    Island: Island | None
    Artifact: Artifact | None
