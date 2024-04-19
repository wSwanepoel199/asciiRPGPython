from __future__ import annotations
from typing import Iterable, Any, TYPE_CHECKING
import tcod
from src.event_handler import EventHandler

if TYPE_CHECKING:
  from src.entity import Entity
  from src.map import GameMap

class Engine:
  game_map: GameMap
  def __init__(self, player: Entity) -> None:
    self.player = player
    self.console: tcod.console.Console = {}
    self.context: tcod.context.Context = {}
    self.event_handler: EventHandler = EventHandler(engine=self)

  def handle_enemy_turn(self) -> None:
    for entity in self.game_map.entities - {self.player}:
      if entity.ai:
        entity.ai.perform()

  # def handle_event(self, events: Iterable[Any]) -> None:
  #   for event in events:
  #     action = self.event_handler.dispatch(event=event)

  #     if action is None:
  #       continue

  #     action.perform(engine=self, entity=self.player)
  #     self.handle_enemy_turn()
  #     self.update_fov()

  def update_fov(self) -> None:
    """Recompute the visible area based on the players point of view."""
    self.game_map.seeing[:] = tcod.map.compute_fov(
      transparency=self.game_map.tiles['transparent'],
      pov=(self.player.x, self.player.y),
      radius=8
    )

    # If a tile is "seeing" it should be added to "seen".
    self.game_map.seen |= self.game_map.seeing

  def render(self) -> None:
    self.console.clear()
    self.game_map.render(console=self.console)

    self.context.present(console=self.console)

  def createConsole(self, width:int, height:int, tileset_image:str, tileset_width:int, tileset_height:int ) -> None:

    tileset = tcod.tileset.load_tilesheet(
    path=tileset_image,
    columns=tileset_width, rows=tileset_height,
    charmap=tcod.tileset.CHARMAP_TCOD
    )
    
    self.console = tcod.console.Console(width=width, height=height, order="F")
    self.context = tcod.context.new_terminal(
    columns=width,
    rows=height,
    tileset=tileset,
    title="Rogue but worse",
    vsync=True,
    )