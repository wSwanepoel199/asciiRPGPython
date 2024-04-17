from enum import Enum

player = {
  "name": '',
  "HP": 10,
  "MAX_HP": 10,
  "ATK": 2,
  "potions": 1,
  "elixirs": 0,
  "money": 0,
  "x": 0,
  "y": 0,
  "key": False,
  "combat": False,
}

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
  ):
    arg = {
      "enitityType": "",
      'icon': '.',
      'colour': 'white',
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

  def __str__(self):
    return f"{self.__dict__}"

  def __setitem__(self, key, value):
    print(value, key)
    setattr(self, key, value)

  def __getitem__(self, key):
    return getattr(self, key)
  
  def items(self):
    return self.__dict__.items()
  
  def moveEntity(self, x, y):
    self.x = x
    self.y = y


enemy_stats = {
  # "Goblin": {
  #   "hp": 15,
  #   "atk": 3,
  #   "gold": 8,
  #   "spawn": 30
  # },
  "Goblin" : Entity({
    'enitityType': 'ENEMY',
    'icon': "G",
    'colour': 'green',
    'name': 'Goblin',
    'HP': 15,
    'ATK': 3,
    'money': 8,
    'spawn': 30
  }),
  # "Orc": {
  #   "hp": 35,
  #   "atk": 5,
  #   "gold": 18,
  #   "spawn": 10
  # },
  "Orc" : Entity({
    'enitityType': 'ENEMY',
    'icon': "O",
    'colour': 'grey',
    'name': 'Orc',
    'HP': 35,
    'ATK': 5,
    'money': 18,
    'spawn': 10
  }),
  # "Slime": {
  #   "hp": 30,
  #   "atk": 2,
  #   "gold": 12,
  #   "spawn": 20,
  # },
  "Slime" : Entity({
    'enitityType': 'ENEMY',
    "icon": "S",
    'colour': 'blue',
    'name': 'Slime',
    'HP': 30,
    'ATK': 2,
    'money': 18,
    'spawn': 20
  }),
  # "Dragon": {
  #   "hp": 100,
  #   "atk": 8,
  #   "gold": 100,
  #   "spawn": 100
  #   },
  "Dragon" : Entity({
  'enitityType': 'ENEMY',
  'icon': 'D',
  'colour': 'red',
  'name': 'Dragon',
  'HP': 100,
  'ATK': 8,
  'money': 100,
  'spawn': 100
  }),
}
