from __future__ import annotations

import copy
from typing import  Optional, Tuple, TypeVar, TYPE_CHECKING, Any, Type
# from src.components.ai import BaseAi



if TYPE_CHECKING:
    from src.components.ai import BaseAi
    from src.components.fighter import Fighter
    from src.map import GameMap
    from src.engine import Engine

T = TypeVar("T", bound="Entity")

# class EntityList(Enum):
#   OBJECT = '.'
#   PLAYER = "@"
#   GOBLIN = "G"
#   SLIME = "S"
#   ORC = "O"
#   DRAGON = "D"

class Entity:
  parent: GameMap
  def __init__(
    self,
    parent: Optional[GameMap] = None,
    entityType: str = "",
    char: str = "?",
    colour: Tuple[int,int,int] = (255,255,255),
    name: str= "<Unnamed>",
    inventory: dict = {},
    money: int= 0,
    x: int=0,
    y: int=0,
    location:str= "overworld",
    safe: bool= True,
    key: bool=False,
    combat: bool=False,
    blocks_movement: bool= False,
  ) -> None:
    self.entityType = entityType
    self.char= char
    self.colour = colour
    self.name = name
    self.inventory = inventory
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
    if not gamemap:
      return
    if hasattr(self, 'parent'):
      if self.parent is self.gamemap:
        self.gamemap.entities.remove(self)
    self.parent = gamemap
    gamemap.entities.add(self)

class Actor(Entity):
  def __init__(
      self, 
      *,
      entityType: str = 'ACTOR',
      money:int= 0,
      x:int = 0,
      y:int = 0,
      char:str="?",
      colour: Tuple[int,int,int]=(255,255,255),
      name: str= "<Unnamed>",
      ai_cls: Type[BaseAi],
      fighter: Fighter,
    ) -> None:
    super().__init__(
      entityType=entityType,
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

  @property
  def alive(self)->bool:
    return bool(self.ai)

# enemy_stats = {
#   "Goblin" : entity_factory.goblin,
#   "Orc" : entity_factory.orc,
#   "Slime" : entity_factory.slime,
#   "Dragon" : entity_factory.dragon,
# }
