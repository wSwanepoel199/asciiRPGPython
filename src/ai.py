from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from src.actions import Action, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
  from src.actions import Action
  from src.entity import Entity, Actor
  from src.engine import Engine
  from src.map import GameMap

class BaseAi(Action):
  # entity: Actor

  def perform(self) -> None:
    raise NotImplementedError

  def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
    """
    Compute and return a path to the target position.

    If there is no valid path then returns an empty list.
    """
    # Copy the walkable array.
    cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

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
    pathfinder = tcod.path.Pathfinder(graph)

    pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

    # Compute the path to the destination and remove the starting point.
    path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

    # Convert from List[List[int]] to List[Tuple[int, int]].
    return [(index[0], index[1]) for index in path]
  
class HostileAi(BaseAi):
  def __init__(self, entity:Actor):
    super().__init__(entity=entity)
    self.path: List[Tuple[int,int]] = []
  
  def perform(self) -> None:
    target = self.engine.player
    dx = target.x - self.entity.x
    dy = target.y - self.entity.y

    distance = max(abs(dx), abs(dy)) # Chebyshev distance.

    if self.engine.game_map.seeing[self.entity.x, self.entity.y]:
      if distance <= 1:
        return MeleeAction(entity=self.entity, dx=dx, dy=dy).perform()

      self.path = self.get_path_to(dest_x=target.x, dest_y=target.y)

    if self.path:
      dest_x, dest_y = self.path.pop(0)
      return MovementAction(
        entity=self.entity, dx=dest_x - self.entity.x, dy=dest_y - self.entity.y,
      ).perform()

    return WaitAction(entity=self.entity).perform()