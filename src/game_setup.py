"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy, tcod
import tcod.constants
from typing import Optional

import src.factory.actor_factory as actor_factory
import src.event_handler as event_handler
from src.engine import Engine
from src.procgen import genDungeon

def new_game(engine: Engine, map_w:int ,map_h:int, map_max_rooms:int, room_min_size:int, room_max_size:int, max_enemies:int, max_items:int) -> None:
  """Start a new game."""
  map_width = map_w-(map_w // 4)
  map_height = map_h
  squareMapDimMin = min(map_width, map_height)

  room_size_min = room_min_size
  room_size_max = room_max_size
  max_rooms = map_max_rooms

  room_max_enemy = max_enemies
  room_max_item = max_items

  engine.player = copy.deepcopy(actor_factory.player)
  
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
  def on_render(self, console: tcod.console.Console) -> None:
    # console = self.engine.console
    bg_image = tcod.image.load(filename="./src/assets/menu_background.png")[:,:,:3]
    colours = self.engine.colours
    console.draw_semigraphics(pixels=bg_image,x=0,y=0)

    console.print(
      x=console.width // 2,
      y=console.height // 2 - 4,
      string=self.engine.title,
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
    if len(self.engine.title)>10:
      menu_width = len(self.engine.title)
    else:
      menu_width = 10
      
    for i, text in enumerate(
      self.engine.message_log.wrap(
        string=f"[N]ew game,\n[C]ontinue,\n[Q]uit",
        width=menu_width
      )):
      console.print(
        x=console.width // 2,
        y=console.height // 2 - 2 + i*2,
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
          engine= self.engine,
          map_w=self.engine.console.width, 
          map_h=self.engine.console.height, 
          map_max_rooms=30, 
          room_min_size=6, 
          room_max_size=10, 
          max_enemies=2, 
          max_items=2,
        ))
      case tcod.event.KeySym.c:
        pass
      case tcod.event.KeySym.q:
        raise SystemExit()
      case tcod.event.KeySym.ESCAPE:
        raise SystemExit()
      case _:
        return None