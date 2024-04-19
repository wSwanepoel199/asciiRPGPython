from __future__ import annotations

import copy
from typing import  Optional, Tuple, TypeVar, TYPE_CHECKING, Any, Type
from src.ai import BaseAi
import src.factory.entity_factory as entity_factory

if TYPE_CHECKING:
    from src.map import GameMap

T = TypeVar("T", bound="Entity")

# class EntityList(Enum):
#   OBJECT = '.'
#   PLAYER = "@"
#   GOBLIN = "G"
#   SLIME = "S"
#   ORC = "O"
#   DRAGON = "D"

class Entity:
  gamemap: GameMap
  def __init__(
    self,
    gamemap: Optional[GameMap] = None,
    entityType: str = "",
    char: str = "?",
    colour: Tuple[int,int,int] = (255,255,255),
    name: str= "<Unnamed>",
    HP: int = 0,
    ATK: int =0,
    DEF: int= 0,
    inventory: dict = {},
    money: int= 0,
    x: int=0,
    y: int=0,
    location:str= "overworld",
    safe: bool= True,
    key: bool=False,
    combat: bool=False,
    blocks_movement: bool= False,
    args = {}
  ) -> None:
    # arg = {
    #   "entityType": "",
    #   'char': '.',
    #   'colour': (255,255,255),
    #   "name": "",
    #   "HP": 0,
    #   "ATK": 0,
    #   'inventory':{},
    #   "money": 0,
    #   "x": 0,
    #   "y": 0,
    #   "location": "overworld",
    #   "safe": True,
    #   "key": False,
    #   "combat": False,
    #   "blocks_movement": False
    # }
    # arg.update(args)

    # for key, value in arg.items():
    #   self[key] = value
    self.entityType = entityType
    self.char= char
    self.colour = colour
    self.name = name
    self.HP = HP
    self.MAX_HP = self.HP
    self.ATK = ATK
    self.DEF = DEF
    self.inventory = inventory
    self.money=money
    self.x=x
    self.y=y
    self.location=location
    self.safe=safe
    self.key=key
    self.combat =combat
    self.blocks_movement = blocks_movement

    if gamemap:
      self.gamemap = gamemap
      gamemap.entities.add(self)


  def __str__(self) -> str:
    return f"{self.__dict__}"

  def __setitem__(self, key, value) -> None:
    setattr(self, key, value)

  def __getitem__(self, key) -> Any:
    return getattr(self, key)

  def items(self) -> Any:
    return self.__dict__.items()

  def move(self, dx:int, dy:int) -> None:
    self.x += dx
    self.y += dy

  def spawn(self: T, gamemap: GameMap, x: int, y:int) -> T:
    """Spawn a copy of this instance at the given location."""
    print(self, gamemap, x, y)
    clone = copy.deepcopy(self)
    clone.x = x
    clone.y = y
    clone.gamemap = gamemap
    gamemap.entities.add(clone)
    return clone

  def place(self, x:int, y:int, gamemap: Optional[GameMap] = None) -> None:
    self.x = x
    self.y = y
    if not gamemap:
      return
    if hasattr(self,'gamemap'):
      self.gamemap.entities.remove(self)
    self.gamemap = gamemap
    gamemap.entities.add(self)

class Actor(Entity):
  def __init__(
      self, 
      *,
      entityType: str = 'ACTOR',
      HP:int = 0,
      ATK:int= 0,
      DEF:int=0,
      money:int= 0,
      x:int = 0,
      y:int = 0,
      char:str="?",
      colour: Tuple[int,int,int]=(255,255,255),
      name: str= "<Unnamed>",
      ai_cls: Type[BaseAi],
    ) -> None:
    super().__init__(
      entityType=entityType,
      HP=HP,
      ATK=ATK,
      DEF=DEF,
      money=money,
      x=x,
      y=y,
      char=char,
      colour=colour,
      name=name,
      blocks_movement=True
    )
    self.ai: Optional[BaseAi] = ai_cls(self)
  
  @property
  def alive(self)->bool:
    return bool(self.ai)

# enemy_stats = {
#   "Goblin" : entity_factory.goblin,
#   "Orc" : entity_factory.orc,
#   "Slime" : entity_factory.slime,
#   "Dragon" : entity_factory.dragon,
# }
