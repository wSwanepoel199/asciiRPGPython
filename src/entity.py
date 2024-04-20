from __future__ import annotations

import copy, math
from typing import  Optional, Tuple, TypeVar, TYPE_CHECKING, Any, Type, Union

from src.components.inventory import Inventory


if TYPE_CHECKING:
    from src.components.ai import BaseAi
    from src.components.fighter import Fighter
    from src.components.consumable import Consumable
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
  parent: Union[GameMap, Inventory]
  def __init__(
    self,
    parent: Optional[GameMap] = None,
    entity_type: str = "",
    char: str = "?",
    colour: Tuple[int,int,int] = (255,255,255),
    name: str= "<Unnamed>",
    money: int= 0,
    x: int=0,
    y: int=0,
    location:str= "overworld",
    safe: bool= True,
    key: bool=False,
    combat: bool=False,
    blocks_movement: bool= False,
  ) -> None:
    self.entity_type = entity_type
    self.char= char
    self.colour = colour
    self.name = name
    self.money=money
    self.x=x
    self.y=y
    self.location=location
    self.safe=safe
    self.key=key
    self.combat =combat
    self.blocks_movement = blocks_movement
    self.target: Optional[Entity] = None
    if parent:
      self.parent = parent
      parent.entities.add(self)
  @property
  def gamemap(self) -> GameMap:
    return self.parent.gamemap

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
    clone = copy.deepcopy(x=self)
    clone.x = x
    clone.y = y
    clone.parent = gamemap
    gamemap.entities.add(clone)
    return clone

  def place(self, x:int, y:int, gamemap: Optional[GameMap] = None) -> None:
    self.x = x
    self.y = y
    if gamemap:
      if hasattr(self, 'parent'):
        if self.parent is self.gamemap:
          self.gamemap.entities.remove(self)
    self.parent = gamemap
    gamemap.entities.add(self)
  
  def distance(self, x:int, y:int) -> float:
    return math.sqrt((x-self.x)**2+(y-self.y)**2)

class Actor(Entity):
  def __init__(
      self, 
      *,
      entity_type: str = 'ACTOR',
      money:int= 0,
      x:int = 0,
      y:int = 0,
      char:str="?",
      colour: Tuple[int,int,int]=(255,255,255),
      name: str= "<Unnamed>",
      ai_cls: Type[BaseAi],
      fighter: Fighter,
      inventory: Inventory = Inventory(capacity=0),
    ) -> None:
    super().__init__(
      entity_type=entity_type,
      money=money,
      x=x,
      y=y,
      char=char,
      colour=colour,
      name=name,
      blocks_movement=True
    )
    self.ai: Optional[BaseAi] = ai_cls(self)
    self.fighter = fighter
    self.fighter.parent = self

    self.inventory = inventory
    self.inventory.parent = self

  @property
  def alive(self)->bool:
    return bool(self.ai)

class Item(Entity):
  def __init__(
    self,
    *,
    x:int=0,
    y:int=0,
    char:str="?",
    colour: Tuple[int,int,int]=(255,255,255),
    name: str= "<Unnamed>",
    entity_type: str= "ITEM",
    consumable: Consumable,
  ):
    super().__init__(
      x=x,
      y=y,
      char=char,
      colour=colour,
      name=name,
      blocks_movement=False,
      entity_type=entity_type
    )
    self.consumable = consumable
    self.consumable.parent = self