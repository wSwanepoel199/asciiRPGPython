from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.map import GameMap

# T = TypeVar("T", bound="Entity")

# class EntityList(Enum):
#   OBJECT = '.'
#   PLAYER = "@"
#   GOBLIN = "G"
#   SLIME = "S"
#   ORC = "O"
#   DRAGON = "D"

class Entity:
  def __init__(
    self,
    args = {}
  ) -> None:
    arg = {
      "entityType": "",
      'char': '.',
      'colour': (255,255,255),
      "name": "",
      "HP": 0,
      "ATK": 0,
      'inventory':{},
      "money": 0,
      "x": 0,
      "y": 0,
      "location": "overworld",
      "safe": True,
      "key": False,
      "combat": False,
      "blocks_movement": False
    }
    arg.update(args)

    for key, value in arg.items():
      self[key] = value

    self.MAX_HP = self.HP

  def __str__(self) -> str:
    return f"{self.__dict__}"

  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key) -> Any:
    return getattr(self, key)

  def items(self) -> Any:
    return self.__dict__.items()

  def move(self, dx, dy) -> None:
    self.x += dx
    self.y += dy

  def spawn(self: Entity, gamemap: GameMap, x: int, y:int) -> Entity:
    """Spawn a copy of this instance at the given location."""
    print(self, gamemap, x, y)
    clone = copy.deepcopy(self)
    clone.x = x
    clone.y = y
    gamemap.entities.add(clone)
    return clone


enemy_stats = {
  "Goblin" : Entity(args={
    'entityType': 'ENEMY',
    "char": "G",
    "colour": (0,200,0),
    "name": 'Goblin',
    "HP": 15,
    'ATK': 3,
    'money': 8,
    'blocks_movement':True
  }),
  "Orc" : Entity(args={
    'entityType': 'ENEMY',
    'char': "O",
    'colour': (200,200,200),
    'name': 'Orc',
    'HP': 35,
    'ATK': 5,
    'money': 18,
    'blocks_movement':True
  }),
  "Slime" : Entity(args={
    'entityType': 'ENEMY',
    "char": "S",
    'colour': (0, 133, 235),
    'name': 'Slime',
    'HP': 30,
    'ATK': 2,
    'money': 18,
    'blocks_movement':True
  }),
  "Dragon" : Entity(args={
    'entityType': 'ENEMY',
    'char': 'D',
    'colour': (210,0,0),
    'name': 'Dragon',
    'HP': 100,
    'ATK': 8,
    'money': 100,
    'blocks_movement':True
  }),
}
