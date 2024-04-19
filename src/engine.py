from __future__ import annotations
from typing import Iterable, Any, TYPE_CHECKING
import tcod
from src.event_handler import MainGameEventHandler

if TYPE_CHECKING:
  from src.entity import Actor
  from src.map import GameMap
  from src.event_handler import EventHandler

class Engine:
  game_map: GameMap
  def __init__(self, player: Actor) -> None:
    self.player = player
    self.console: tcod.console.Console = {}
    self.context: tcod.context.Context = {}
    self.event_handler: EventHandler = MainGameEventHandler(engine=self)

  def handle_enemy_turn(self) -> None:
    for entity in self.game_map.entities - {self.player}:
      if entity.ai:
        entity.ai.perform()

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
    if self.player.HP>0:
      self.console.print(
        x=1,
        y=0,
        string=f"HP: {self.player.HP}/{self.player.MAX_HP}",
      )
    else :
      self.console.print(
        x=1,
        y=0,
        string="YOU DIED!",
      )
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