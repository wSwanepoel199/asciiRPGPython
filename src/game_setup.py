"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy, tcod
import tcod.constants
from typing import Optional

import src.factory.actor_factory as actor_factory
import src.event_handler as event_handler
from src.engine import Engine
from src.procgen import genDungeon

# bg_image = tcod.image.load(filename="assets/background.png")[:,:,:3]

def new_game(map_w:int,map_h:int, map_max_rooms:int, room_min_size:int, room_max_size:int, max_enemies:int, max_items:int, tileset_image:str, tileset_width:int, tileset_height:int) -> Engine:
  """Start a new game."""
  map_width = map_w
  map_height = map_h
  squareMapDimMin = min(map_width, map_height)

  room_size_min = room_min_size
  room_size_max = room_max_size
  max_rooms = map_max_rooms

  room_max_enemy = max_enemies
  room_max_item = max_items

  player = copy.deepcopy(actor_factory.player)

  engine = Engine(
    width=map_width,
    height=map_height,
    tileset_image=tileset_image,
    tileset_width=tileset_width,
    tileset_height=tileset_height
  )

  engine.player = player

  engine.game_map = genDungeon(
    limit=max_rooms,
    min=room_size_min,
    max=room_size_max,
    w=squareMapDimMin,
    h=squareMapDimMin,
    enemy_limit=room_max_enemy,
    item_limit=room_max_item,
    engine=engine
  )
  engine.update_fov()

  engine.message_log.add_message(
    text="Hello and welcome, adventurer, to yet another dungeon!",
    fg=engine.colours['welcome_text']
  )

  return engine

class MainMenu(event_handler.BaseEventHandler):
  """Handle the main menu rendering and input."""
  def __init__(self, engine: Engine, width: int, height: int, tileset_image: str, tileset_width: int, tileset_height: int) -> None:
    super().__init__(engine=engine)
    self.width = width
    self.height = height
    self.tileset_image = tileset_image
    self.tileset_width = tileset_width
    self.tileset_height = tileset_height
  def on_render(self) -> None:
    console = self.engine.console
    colours = self.engine.colours
    # console.draw_semigraphics(pixels=bg_image,x=0,y=0)

    console.print(
      x=console.width // 2,
      y=console.height // 2 - 4,
      string="TOMBS OF THE ANCIENT KINGS",
      fg=colours['menu_title'],
      alignment=tcod.constants.CENTER,
    )
    console.print(
      x=console.width // 2,
      y=console.height - 2,
      string="By wSwanepoel",
      fg=colours['menu_title'],
      alignment=tcod.constants.CENTER
    )

    menu_width = 24
    for i, text in enumerate(
      ["[N]ew game", "[C]ontinue adventure", "[Q]uit"]
    ):
      console.print(
        x=console.width // 2,
        y=console.height // 2 - 2 + i,
        string=text.ljust(menu_width),
        fg=colours['menu_title'],
        bg=colours['black'],
        alignment=tcod.constants.CENTER,
        bg_blend=tcod.constants.BKGND_ALPH
      )
  
  def ev_keydown(
      self, event: tcod.event.KeyDown
  ) -> Optional[event_handler.BaseEventHandler]:
    match event.sym:
      case tcod.event.KeySym.n:
        return event_handler.MainGameEventHandler(engine=new_game(
          map_w=self.width, 
          map_h=self.height, 
          map_max_rooms=30, 
          room_min_size=6, 
          room_max_size=10, 
          max_enemies=2, 
          max_items=2,
          tileset_image=self.tileset_image,
          tileset_width=self.tileset_width,
          tileset_height=self.tileset_height
        ))
      case tcod.event.KeySym.c:
        pass
      case tcod.event.KeySym.q:
        raise SystemExit()
      case tcod.event.KeySym.ESCAPE:
        raise SystemExit()
      case _:
        return None