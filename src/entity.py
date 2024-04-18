from _collections_abc import dict_items
from typing import Any

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
      "spawn": 0,
      "location": "overworld",
      "safe": True,
      "key": False,
      "combat": False
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


enemy_stats = {
  "Goblin" : Entity(args={
    'entityType': 'ENEMY',
    'char': "G",
    'colour': (0,100,0),
    'name': 'Goblin',
    'HP': 15,
    'ATK': 3,
    'money': 8,
    'spawn': 30
  }),
  "Orc" : Entity(args={
    'entityType': 'ENEMY',
    'char': "O",
    'colour': (100,100,100),
    'name': 'Orc',
    'HP': 35,
    'ATK': 5,
    'money': 18,
    'spawn': 10
  }),
  "Slime" : Entity(args={
    'entityType': 'ENEMY',
    "char": "S",
    'colour': (0,0,110),
    'name': 'Slime',
    'HP': 30,
    'ATK': 2,
    'money': 18,
    'spawn': 20
  }),
  "Dragon" : Entity(args={
    'entityType': 'ENEMY',
    'char': 'D',
    'colour': (110,0,0),
    'name': 'Dragon',
    'HP': 100,
    'ATK': 8,
    'money': 100,
    'spawn': 100
  }),
}
