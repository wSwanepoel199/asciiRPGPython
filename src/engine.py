from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple
import tcod, traceback, lzma, pickle
import tcod.constants
from src.utils.colour import loadColours
from src.message import MessageLog
import src.utils.exceptions as exceptions
import src.event_handler as event_handler

if TYPE_CHECKING:
  from src.entity import Actor
  from src.map import GameMap, GameWorld

class Engine:
  game_map: GameMap
  game_world: GameWorld
  def __init__(self, player: Actor = None) -> None:
    self.player = player
    self.title = None
    self.mouse_location = (0,0)
    self.event_handler: Optional[event_handler.EventHandler] = None
    self.message_log = MessageLog()
  @property
  def side_console(self) -> int:
    if self.console.width:
      return self.console.width-self.game_world.viewport_width
    else:
      return 20
  @property
  def colours(self) -> dict:
    return loadColours()
  @property
  def exceptions(self) -> exceptions:
    return exceptions
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
    self.game_map.visible[:] = tcod.map.compute_fov(
      transparency=self.game_map.tiles['transparent'],
      pov=(self.player.x, self.player.y),
      radius=8
    )

    # If a tile is "visible" it should be added to "explored".
    self.game_map.explored |= self.game_map.visible

  def handle_deaths(self) -> None:
    for entity in self.game_map.actors:
      if entity.ai and entity.fighter.HP <= 0:
        entity.fighter.die()

  def save_as(self, filename: str) -> None:
    if not isinstance(self.event_handler, event_handler.GameOverEventHandler):
      self.event_handler = event_handler.MainGameEventHandler(engine=self)
    if self.context:
      self.context = None
    save_data = lzma.compress(data=pickle.dumps(obj=self))
    with open(file=filename, mode="wb") as f:
      f.write(save_data)

  def render(self, console: tcod.console.Console) -> None:
    self.console = console
    # Draw Side Window

    width, height = self.context.recommended_console_size()
    self.game_world.viewport_width = width-min((width // 3), 55)
    self.game_world.viewport_height = height
    self.game_map.render(console=console)

    self.genWindow(
      x=self.game_world.viewport_width,
      y=0,
      width=self.side_console,
      height=console.height
    )

    if self.side_console > 20:
      bar_width = 20
    else:
      bar_width = self.side_console-4
    
    y = 1

    # Display Player HP
    if self.player.fighter.HP > 0:
      for line in list(self.message_log.wrap(
        string=f"Dungeon level: {self.game_world.current_floor}",
        width=self.side_console-2
      )):
        self.console.print(
          x=self.game_world.viewport_width+1,
          y=y,
          string=line
        )
        y+=1
      y +=1
      console.print(
        x=self.game_world.viewport_width+1,
        y=y,
        string=f"{self.player.name} HP:"
      )
      y+=1
      self.render_bar(
        bar_x=self.game_world.viewport_width+2,
        bar_y=y,
        curr_val=self.player.fighter.HP,
        max_val=self.player.fighter.MAX_HP,
        total_width=bar_width,
        bar_fg=self.colours['hp_bar_filled'],
      )
      y +=2
      if self.player.level:
        self.render_bar(
          bar_x=self.game_world.viewport_width+2,
          bar_y=y,
          curr_val=self.player.level.curr_xp,
          max_val=self.player.level.xp_to_next_level,
          total_width=bar_width,
          bar_fg=self.colours['xp_bar_filled'],
        )
        text = "XP"
        console.print(
          x=self.game_world.viewport_width+2+bar_width-len(text),
          y=y,
          string=text
        )
        y +=2
    # Display Player Target HP
    if self.player.target and self.player.target.alive and self.player.alive:
      target_name= f"{self.player.target.name} HP: "
      if self.side_console <= 50:
        y +=1
        x = self.game_world.viewport_width
        console.print(
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
          bar_fg=self.colours['enemy_hp_bar_filled'],
        )
        y+=2
      else:
        y = 3
        x = console.width
        console.print(
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
        y+=2
    # Display If Player is dead
    if self.player.fighter.HP <= 0:
      msg= "YOU DIED!"
      console.print(
        x= self.game_world.viewport_width + round(number=(self.side_console - len(msg)-1)/2) ,
        y=5,
        string=msg,
      )
    else:
      # render names if entities under mouse
      y+=1
      self.render_names_at_mouse(
        x=self.game_world.viewport_width+1,
        y=y,
        width=self.side_console-2,
        height=self.console.height//3 - 3
      )


    event_log_height = self.console.height // 3 * 2
    # Event Log
    self.draw_line(
      x=self.game_world.viewport_width,
      y=event_log_height,
      width=self.side_console,
      title="┤Events├",
      alignment=tcod.constants.CENTER
    )
    self.message_log.render(
      console=console,
      x=self.game_world.viewport_width+1,
      y=event_log_height + 1,
      width=self.side_console-2,
      height=self.console.height-event_log_height - 2
    )
  def genContext(
      self, 
      width:int, 
      height:int, 
      tileset: tcod.tileset.Tileset, 
      title:str, 
      columns:Optional[int] = None,
      rows: Optional[int] = None,
      vsync: Optional[bool] = None, 
      context: Optional[tcod.context.Context] = None,
      console: Optional[tcod.console.Console] = None,
    ) -> tcod.context.Context:
    if context:
      self.context = context
    else:
      self.context = tcod.context.new(
        width=width,
        height=height,
        # columns=columns,
        # rows=rows,
        tileset=tileset,
        title=title,
        sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE,
      )
    return self.context
  def genConsole(self, console: Optional[tcod.console.Console] = None, width:int=0, height:int=0 ) -> tcod.console.Console:
    if console:
      self.console = console
    else:
      self.console = tcod.console.Console(width=width, height=height, order="F")
    
    return self.console
  
  def addTileset(self, tileset_image:str, tileset_width:int, tileset_height:int) -> None:
    tileset = tcod.tileset.load_tilesheet(
    path=tileset_image,
    columns=tileset_width, rows=tileset_height,
    charmap=tcod.tileset.CHARMAP_TCOD
    )
    self.context.change_tileset(tileset=tileset)

  def render_bar(
      self, 
      bar_x:int = 0, 
      bar_y:int = 0, 
      bar_text: str = '', 
      curr_val: int = 0, 
      max_val:int = 0, 
      total_width:int = 0, 
      flip:bool = False,
      bar_fg: Tuple[int,int,int] = (0, 96, 0),
      bar_bg: Tuple[int,int,int] = (23, 23, 23),
  ) -> None:

    if(flip):
      bar_width = total_width - int(float(curr_val) / max_val * total_width)
      bar_bg = bar_fg
      bar_fg = bar_bg
    else:
      bar_width = int(float(curr_val) / max_val * total_width)
      bar_fg = bar_fg
      bar_bg = bar_bg
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