from __future__ import annotations

from typing import List, Tuple, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod, random

from src.actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction
from src.entity import Actor

if TYPE_CHECKING:
  from src.actions import Action
  from src.entity import Actor

class BaseAi(Action):
  def __init__(self, entity: Actor):
    super().__init__(entity=entity)
    # if(self.entity.fighter.HP <= 0):
    #   self.entity.fighter.die()
    #   return

  def perform(self) -> None:
    raise NotImplementedError()

  def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
    """
    Compute and return a path to the target position.

    If there is no valid path then returns an empty list.
    """
    # Copy the walkable array.
    cost = np.array(object=self.entity.gamemap.tiles["walkable"], dtype=np.int8)

    for entity in self.entity.gamemap.entities:
      # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
      if entity.blocks_movement and cost[entity.x, entity.y]:
        # Add to the cost of a blocked position.
        # A lower number means more enemies will crowd behind each other in
        # hallways.  A higher number means enemies will take longer paths in
        # order to surround the player.
        cost[entity.x, entity.y] += 10

    # Create a graph from the cost array and pass that graph to a new pathfinder.
    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
    pathfinder = tcod.path.Pathfinder(graph=graph)

    pathfinder.add_root(index=(self.entity.x, self.entity.y))  # Start position.

    # Compute the path to the destination and remove the starting point.
    path: List[List[int]] = pathfinder.path_to(index=(dest_x, dest_y))[1:].tolist()

    # Convert from List[List[int]] to List[Tuple[int, int]].
    return [(index[0], index[1]) for index in path]
  
class HostileAi(BaseAi):
  def __init__(self, entity:Actor):
    super().__init__(entity=entity)
    self.path: List[Tuple[int,int]] = []
    self.memory = 0
    self.last_seen = (self.entity.x, self.entity.y)

  def perform(self) -> None:

    target = self.engine.player
    dx = 0
    dy = 0
    if self.engine.game_map.visible[self.entity.x, self.entity.y]:
      dx = target.x - self.entity.x
      dy = target.y - self.entity.y
    elif self.engine.game_map.explored[self.entity.x, self.entity.y] and self.memory > 0:
      self.memory -= 1
      dx = self.last_seen[0] - self.entity.x
      dy = self.last_seen[1] - self.entity.y

    distance = max(abs(dx), abs(dy)) # Chebyshev distance.
    if self.engine.game_map.visible[self.entity.x, self.entity.y]:
      if distance <= 1:
        return MeleeAction(entity=self.entity, dx=dx, dy=dy).perform()
      if distance <= 5:
        self.last_seen = (target.x, target.y)
        self.memory = 5
      if distance > 1 and distance < 5:
        self.path = self.get_path_to(dest_x=self.last_seen[0], dest_y=self.last_seen[1])
    elif self.memory > 0 and (not self.entity.x == self.last_seen[0] and not self.entity.y == self.last_seen[1]):
      self.path = self.get_path_to(dest_x=self.last_seen[0], dest_y=self.last_seen[1])

    if self.path:
      dest_x, dest_y = self.path.pop(0)
      return MovementAction(
        entity=self.entity, dx=dest_x - self.entity.x, dy=dest_y - self.entity.y,
      ).perform()

    return WaitAction(entity=self.entity).perform()

class ConfusedAi(BaseAi):
  def __init__(self, entity: Actor, prev_ai: Optional[BaseAi], turns_remaining:int):
    super().__init__(entity=entity)
    self.prev_ai = prev_ai
    self.turns_remaining = turns_remaining
  
  def perform(self) ->None:
    if self.turns_remaining <= 0:
      self.engine.message_log.add_message(
        text=f"The {self.entity.name} is no longer confused."
      )
      self.entity.ai = self.prev_ai
    else:
      self.turns_remaining -= 1
      dir_x, dir_y = random.choice(
        [
          (0, -1), 
          (1, 0), 
          (0, 1), 
          (-1, 0)
        ]
      )
      return BumpAction(entity=self.entity, dx=dir_x, dy=dir_y).perform()