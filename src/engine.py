from __future__ import annotations
from typing import Iterable, Any, TYPE_CHECKING, Optional
import tcod, traceback
import tcod.constants
from src.utils.colour import loadColours
from src.message import MessageLog
import src.utils.exceptions as exceptions
import src.event_handler as event_handler

if TYPE_CHECKING:
  from src.entity import Actor
  from src.map import GameMap

class Engine:
  game_map: GameMap
  def __init__(self, player: Actor = None) -> None:
    self.player = player
    self.title = None
    self.colours = loadColours()
    self.exceptions = exceptions
    self.event_handler: event_handler.BaseEventHandler = None
    self.console: tcod.console.Console = {}
    self.context: tcod.context.Context = {}
    self.mouse_location = (0, 0)
    self.message_log = MessageLog(engine=self)
  @property
  def side_console(self) -> int:
    if self.console.width:
      return self.console.width - self.game_map.width
  def handle_enemy_turn(self) -> None:
    for entity in set(self.game_map.actors) - {self.player}:
      if not entity.ai:
        continue
      try:
        entity.ai.perform()
      except self.exceptions.Impossible:
        pass

  def update_fov(self) -> None:
    """Recompute the visible area based on the players point of view."""
    self.game_map.seeing[:] = tcod.map.compute_fov(
      transparency=self.game_map.tiles['transparent'],
      pov=(self.player.x, self.player.y),
      radius=8
    )

    # If a tile is "seeing" it should be added to "seen".
    self.game_map.seen |= self.game_map.seeing

  def render(self, console: tcod.console.Console) -> None:
    self.console = console

    self.game_map.render(console=self.console)

    # Draw Side Window
    self.genWindow(
      x=self.game_map.width,
      y=0,
      width=self.side_console,
      height=self.console.height
    )

    if self.side_console > 20:
      bar_width = 20
    else:
      bar_width = self.side_console-4
    
    y = 1

    # Display Player HP
    if self.player.fighter.HP > 0:
      self.console.print(
        x=self.game_map.width+1,
        y=y,
        string=f"{self.player.name} HP:"
      )
      y+=1
      self.render_bar(
        bar_x=self.game_map.width+2,
        bar_y=y,
        curr_val=self.player.fighter.HP,
        max_val=self.player.fighter.MAX_HP,
        total_width=bar_width,
      )
      y +=1
    # Display Player Target HP
    if self.player.target and self.player.target.alive and self.player.alive:
      target_name= f"{self.player.target.name} HP: "
      if self.side_console <= 50:
        x = self.game_map.width
        self.console.print(
          x=x+1,
          y=y,
          string=target_name
        )
        y+=1
        self.render_bar(
          bar_x=x+2,
          bar_y=y,
          curr_val=self.player.target.fighter.HP,
          max_val=self.player.target.fighter.MAX_HP,
          total_width=bar_width,
        )
        y+=1
      else:
        y = 1
        x = self.console.width
        self.console.print(
          x=x-len(target_name)-1,
          y=y,
          string=target_name
        )
        y+=1
        self.render_bar(
          bar_x=x-bar_width-2,
          bar_y=y,
          curr_val=self.player.target.fighter.HP,
          max_val=self.player.target.fighter.MAX_HP,
          total_width=bar_width,
        )
        y+=1
    # Display If Player is dead
    if self.player.fighter.HP <= 0:
      msg= "YOU DIED!"
      self.console.print(
        x= self.game_map.width + round(number=(self.side_console - len(msg)-1)/2) ,
        y=5,
        string=msg,
      )
    # render names if entities under mouse
    y+=1
    self.render_names_at_mouse(
      x=self.game_map.width+1,
      y=y,
      width=self.side_console-2,
      height=5
    )


    # Event Log
    self.draw_line(
      x=self.game_map.width,
      y=round(number=self.console.height/3)*2,
      width=self.side_console,
      title="┤Events├",
      alignment=tcod.constants.CENTER
    )
    self.message_log.render(
      console=self.console,
      x=self.game_map.width+1,
      y=round(number=self.console.height/3)*2+1,
      width=self.side_console-2,
      height=self.console.height-round(number=self.console.height/3)*2-2
    )
  def gameLoop(self) -> None:
    self.console.clear()
    self.event_handler.on_render(console=self.console)
    self.context.present(console=self.console)

    try:
      for event in tcod.event.wait():
        self.context.convert_event(event=event)
        self.event_handler = self.event_handler.handle_events(event=event)
    except Exception:
      traceback.print_exc()
      self.message_log.add_message(
        text=traceback.format_exc(), 
        fg=self.colours['error']
      )
  def genContext(self, width:int, height:int, tileset: tcod.tileset.Tileset, title:str, vsync:bool, context: Optional[tcod.context.Context] = None) -> None:
    if context:
      self.context = context
    else:
      self.context = tcod.context.new_terminal(
        columns=width,
        rows=height,
        tileset=tileset,
        title=title,
        vsync=vsync,
      )
  def genConsole(self, console: Optional[tcod.console.Console] = None, width:int=0, height:int=0 ) -> None:
    if console:
      self.console = console
    else:
      self.console = tcod.console.Console(width=width, height=height, order="F")
    # self.context = tcod.context.new_terminal(
    # columns=width,
    # rows=height,
    # tileset=tileset,
    # title="Rogue but worse",
    # vsync=True,
    # )
  
  def addTileset(self, tileset_image:str, tileset_width:int, tileset_height:int) -> None:
    tileset = tcod.tileset.load_tilesheet(
    path=tileset_image,
    columns=tileset_width, rows=tileset_height,
    charmap=tcod.tileset.CHARMAP_TCOD
    )
    self.context.change_tileset(tileset=tileset)

  def render_bar(self, bar_x:int = 0, bar_y:int = 0, bar_text: str = '', curr_val: int = 0, max_val:int = 0, total_width:int = 0, flip:bool = False) -> None:
    if(flip):
      bar_width = total_width - int(float(curr_val) / max_val * total_width)
      bar_bg = self.colours['bar_filled']
      bar_fg = self.colours['bar_empty']
    else:
      bar_width = int(float(curr_val) / max_val * total_width)
      bar_fg = self.colours['bar_filled']
      bar_bg = self.colours['bar_empty']
    self.console.draw_rect(
      x=bar_x,
      y=bar_y,
      width=total_width,
      height=1,
      ch=1,
      bg=bar_bg
    )
    if bar_width > 0:
      self.console.draw_rect(
        x=bar_x,
        y=bar_y,
        width=bar_width,
        height=1,
        ch=1,
        bg=bar_fg
      )
    if flip:
      msg = f"{curr_val}/{max_val}{bar_text}"
      self.console.print(
        x=self.game_map.width - len(msg) - 1,
        y=bar_y,
        string=msg,
        fg=self.colours['white'],
      )
    else:
      self.console.print(
        x=bar_x,
        y=bar_y,
        string=f"{bar_text}{curr_val}/{max_val}",
        fg=self.colours['white'],
      )
  def genWindow(self, x:int, y:int, width:int, height:int) -> None:
    self.console.draw_frame(
      x=x,
      y=y,
      clear=False,
      width=width,
      height=height,
      fg=self.colours['white'],
    )

  def draw_line(
    self, 
    x:int, 
    y:int, 
    width:int, 
    title:str = "",
    alignment:int = tcod.constants.CENTER
  ) -> None:
    self.console.draw_rect(
      x=x,
      y=y,
      width=width,
      height=1,
      ch=ord('─'),
      fg=self.colours['white']
    )
    self.console.put_char(
      x=x,
      y=y,
      ch=ord('├'),
    )
    self.console.put_char(
      x=x+width-1,
      y=y,
      ch=ord('┤'),
    )
    self.console.print_box(
      x=x+1,
      y=y,
      width=width-2,
      height=1,
      string=title,
      alignment=alignment
    )

  def get_names_at_location(self, x:int, y:int) -> str:
    if not self.game_map.in_bounds(x=x, y=y):
      return ""
    names = ", ".join(
      entity.name
      for entity in self.game_map.entities
      if entity.x == x and entity.y == y
    )
    return names
  
  def render_names_at_mouse(self, x:int, y:int, width:int, height:int) -> None:
    mouse_x,mouse_y = self.mouse_location

    names_at_mouse_local = self.get_names_at_location(x=mouse_x, y=mouse_y)
    # self.console.width - self.game_map.width
    offset = 0
    for line in list(self.message_log.wrap(
      string=names_at_mouse_local, 
      width=width
    )):
      self.console.print(
        x=x,
        y=y+offset,
        string=line
      )
      offset += 1
      if offset > height:
        return