from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from src.entity import Entity
  from src.engine import Engine
  from src.map import GameMap

class BaseComponent:
  parent: Entity

  @property
  def gamemap(self) -> GameMap:
    return self.parent.gamemap

  @property
  def engine(self) -> Engine:
    return self.gamemap.engine
  
  @property
  def viewport(self) -> tuple[int, int]:
    (pos1, pos2)=self.gamemap.get_viewport()
    return pos1