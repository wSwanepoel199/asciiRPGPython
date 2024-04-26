from enum import auto, Enum

class RenderOrder(Enum):
  CORPSE = auto()
  OBJECT = auto()
  ITEM = auto()
  ACTOR = auto()
  PLAYER = auto()