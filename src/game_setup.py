"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy, tcod, lzma, pickle, traceback
import tcod.constants
from typing import Optional

import src.factory.actor_factory as actor_factory
import src.event_handler as event_handler
from src.engine import Engine
from src.procgen import genDungeon
from src.utils.colour import loadColours

def new_game(title:str, width:int, height:int, map_max_rooms:int, room_min_size:int, room_max_size:int, max_enemies:int, max_items:int) -> None:
  """Start a new game."""
  width = width-min((width // 4), 55)
  map_width = width
  map_height = height-2
  squareMapDimMin = min(map_width, map_height)

  room_size_min = room_min_size
  room_size_max = room_max_size
  max_rooms = map_max_rooms

  room_max_enemy = max_enemies
  room_max_item = max_items

  player = copy.deepcopy(actor_factory.player)
  
  engine = Engine(player=player)

  engine.title = title

  engine.game_map = genDungeon(
    room_limit=max_rooms,
    min_room_size=room_size_min,
    max_room_size=room_size_max,
    width= width,
    height= height,
    columns=squareMapDimMin,
    rows=squareMapDimMin,
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

def load_game(filename: str) -> Engine:
  with open(file=filename, mode="rb") as f:
    engine = pickle.loads(lzma.decompress(f.read()))
  assert isinstance(engine, Engine)
  return engine

class MainMenu(event_handler.BaseEventHandler):
  """Handle the main menu rendering and input."""
  def on_render(self, console: tcod.console.Console) -> None:
    # console = self.engine.console
    self.console = console
    self.colours = loadColours()
    image = tcod.image.Image(
      width=console.width,
      height=console.height,
    ).from_file("./src/assets/menu_background.png")
    image.scale(width=console.width*2, height=console.height*2)

    console.draw_semigraphics(pixels=image,x=0,y=0)
    title = "Rogue But Worse"
    console.print(
      x=console.width // 2,
      y=console.height // 2 - 4,
      string=title,
      fg=self.colours['menu_title'],
      alignment=tcod.constants.CENTER,
    )
    console.print(
      x=console.width // 2,
      y=console.height - 2,
      string="By wSwanepoel",
      fg=self.colours['menu_title'],
      alignment=tcod.constants.CENTER
    )
    if len(title)>10:
      menu_width = len(title)
    else:
      menu_width = 10
      
    for i, text in enumerate(
      ["[N]ew game","[C]ontinue","[Q]uit"]
      ):
      console.print(
        x=console.width // 2,
        y=console.height // 2 - 2 + i*2,
        string=text.ljust(menu_width),
        fg=self.colours['menu_title'],
        bg=self.colours['black'],
        alignment=tcod.constants.CENTER,
        bg_blend=tcod.constants.BKGND_ALPH
      )
  
  def ev_keydown(
      self, event: tcod.event.KeyDown
  ) -> Optional[event_handler.BaseEventHandler]:
    match event.sym:
      case tcod.event.KeySym.n:
        return event_handler.MainGameEventHandler(engine=new_game(
          title="Rogue But Worse",
          width=self.console.width,
          height=self.console.height,
          map_max_rooms=30, 
          room_min_size=6, 
          room_max_size=10, 
          max_enemies=2, 
          max_items=2,
        ))
      case tcod.event.KeySym.c:
        try:
          return event_handler.MainGameEventHandler(engine=load_game(filename="savegame.sav"))
        except FileNotFoundError:
          return event_handler.PopupMessage(parent=self, text="No saved game to load.")
        except Exception as exc:
          traceback.print_exc()
          return event_handler.PopupMessage(parent=self, text=f"Failed to load save:\n{exc}")
      case tcod.event.KeySym.q:
        raise SystemExit()
      case tcod.event.KeySym.ESCAPE:
        raise SystemExit()
      case _:
        return None