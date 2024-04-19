from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from src.engine import Engine
  from src.entity import Entity

class Action:
  def __init__(self, entity: Entity) -> None:
    super().__init__()
    self.entity = entity

  @property
  def engine(self) -> Engine:
    """Return the engine this action belongs to."""
    return self.entity.gamemap.engine

  def perform(self) -> None:
    """Perform this action with the objects needed to determine its scope.
    
    `self.engine` is the scope this action is being performed in.
    
    `self.entity` is the object performing the action.
    
    This method must be overridden by Action subclasses.
    """

    raise NotImplementedError()


class EscapeAction(Action):
  def perform(self) -> None:
    raise SystemExit()

class DirectionalAction(Action):
  def __init__(self, entity: Entity, dx:int, dy:int) -> None:
    super().__init__(entity=entity)

    self.dx = dx
    self.dy = dy

  @property
  def dest_xy(self) -> Tuple[int,int]:
    return self.entity.x + self.dx, self.entity.y + self.dy
  
  @property
  def blocking_entity(self) -> Optional[Entity]:
    return self.engine.game_map.get_blocking_entity(*self.dest_xy)
  
  def perform(self) -> None:
    raise NotImplementedError()

class MeleeAction(DirectionalAction):
  def perform(self) -> None:
    target = self.blocking_entity
    if not target:
      return
    
    print(f"You kick the {target.name}, much to your annoyance!")

class MovementAction(DirectionalAction):
  def perform(self) -> None:
    dest_x, dest_y = self.dest_xy

    if not self.engine.game_map.in_bounds(x=dest_x, y=dest_y):
      return
    if not self.engine.game_map.tiles["walkable"][dest_x][dest_y]:
      return
    if self.engine.game_map.get_blocking_entity(x=dest_x, y=dest_y):
      return

    self.entity.move(dx=self.dx, dy=self.dy)

class BumpAction(DirectionalAction):
  def perform(self) -> None:
    if self.blocking_entity:
      return MeleeAction(entity=self.entity, dx=self.dx, dy=self.dy).perform()
    else:
      return MovementAction(entity=self.entity, dx=self.dx, dy=self.dy).perform()

class WaitAction(Action):
  def perform(self) -> None:
    pass