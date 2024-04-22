from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Callable, Tuple, Union

import tcod, os
import tcod.constants

import src.actions as action

if TYPE_CHECKING:
  from src.engine import Engine
  from src.entity import Item

MOVE_KEYS = {
  # Arrow keys.
  tcod.event.KeySym.UP: (0, -1),
  tcod.event.KeySym.DOWN: (0, 1),
  tcod.event.KeySym.LEFT: (-1, 0),
  tcod.event.KeySym.RIGHT: (1, 0),
  tcod.event.KeySym.HOME: (-1, -1),
  tcod.event.KeySym.END: (-1, 1),
  tcod.event.KeySym.PAGEUP: (1, -1),
  tcod.event.KeySym.PAGEDOWN: (1, 1),
  # Numpad keys.
  tcod.event.KeySym.KP_1: (-1, 1),
  tcod.event.KeySym.KP_2: (0, 1),
  tcod.event.KeySym.KP_3: (1, 1),
  tcod.event.KeySym.KP_4: (-1, 0),
  tcod.event.KeySym.KP_6: (1, 0),
  tcod.event.KeySym.KP_7: (-1, -1),
  tcod.event.KeySym.KP_8: (0, -1),
  tcod.event.KeySym.KP_9: (1, -1),
  # Vi keys.
  tcod.event.KeySym.h: (-1, 0),
  tcod.event.KeySym.j: (0, 1),
  tcod.event.KeySym.k: (0, -1),
  tcod.event.KeySym.l: (1, 0),
  tcod.event.KeySym.y: (-1, -1),
  tcod.event.KeySym.u: (1, -1),
  tcod.event.KeySym.b: (-1, 1),
  tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
  tcod.event.KeySym.PERIOD,
  tcod.event.KeySym.KP_5,
  tcod.event.KeySym.CLEAR,
}

CONFIRM_KEYS = {
  tcod.event.KeySym.RETURN,
  tcod.event.KeySym.KP_ENTER,
}

CURSOR_Y_KEYS = {
  tcod.event.KeySym.UP: -1,
  tcod.event.KeySym.DOWN: 1,
  tcod.event.KeySym.PAGEUP: -10,
  tcod.event.KeySym.PAGEDOWN: 10,
}

ActionOrHandler = Union[action.Action, "BaseEventHandler"]

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
  def __init__(self):
    self.console = None,
    self.colours = None
  def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
    state = self.dispatch(event=event)
    if isinstance(state, BaseEventHandler):
      return state
    assert not isinstance(state, action.Action), f"{self!r} can not handle actions."
    return self

  def on_render(self, console: tcod.console.Console) -> None:
    raise NotImplementedError()

  def ev_quit(self, event: tcod.event.Quit) -> Optional[action.Action]:
    raise SystemExit()

class PopupMessage(BaseEventHandler):
  def __init__(self, parent: BaseEventHandler, text:str) -> None:
    self.parent = parent
    self.text = text
  
  def on_render(self, console: tcod.console.Console) -> None:
    self.parent.on_render(console=console)
    console.rgb["fg"]
    console.rgb['bg']

    console.print(
      x=console.width//2,
      y=console.height//2,
      string=self.text,
      fg=self.parent.colours['white'],
      bg=self.parent.colours['black'],
      alignment=tcod.constants.CENTER
    )
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
    return self.parent

class EventHandler(BaseEventHandler):
  def __init__(self, engine: Engine) -> None:
    self.engine = engine
  def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
    action_or_state = self.dispatch(event=event)
    if isinstance(action_or_state, BaseEventHandler):
      return action_or_state
    if self.handle_action(action=action_or_state):
      # A valid action was performed
      if not self.engine.player.alive:
        return GameOverEventHandler(engine=self.engine)
      return MainGameEventHandler(engine=self.engine)
    return self
  
  def handle_action(self, action: Optional[action.Action]) -> bool:
    if action is None:
      return False
    try:
      action.perform()
    except self.engine.exceptions.Impossible as exc:
      self.engine.message_log.add_message(
        text=exc.args[0],
        fg=self.engine.colours['impossible']
      )
      return False
    
    self.engine.handle_enemy_turn()
    self.engine.update_fov()
    return True


  def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
    if self.engine.game_map.in_bounds(x=event.tile.x, y=event.tile.y):
      self.engine.mouse_location = event.tile.x, event.tile.y

  def on_render(self, console: tcod.console.Console) -> None:
    self.engine.render(console=console)

class AskUserEventHandler(EventHandler):
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
    if event.sym in {
      tcod.event.KeySym.LSHIFT,
      tcod.event.KeySym.RSHIFT,
      tcod.event.KeySym.LCTRL,
      tcod.event.KeySym.RCTRL,
      tcod.event.KeySym.LALT,
      tcod.event.KeySym.RALT,
    }:
      return None
    return self.on_exit()
  
  def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
    return self.on_exit()

  def on_exit(self) -> Optional[ActionOrHandler]:
    self.engine.mouse_location = (0, 0)
    return MainGameEventHandler(engine=self.engine)
  
class InventoryEventHandler(AskUserEventHandler):
  TITLE = " INVENTORY "

  def on_render(self, console: tcod.console.Console = None) -> None:
    if console is None:
      console = self.engine.console

    super().on_render(console=console)
    # ─│┌┐└├┤┬┴┼┘
    number_of_items_in_inventory = len(self.engine.player.inventory.items)
    height = 0
    x = self.engine.game_map.width
    y = 0
    width = self.engine.side_console
    offset = 0
    # calculate number of lines wrapped item names use
    if number_of_items_in_inventory > 0:
      lines = []
      for i, item in enumerate(self.engine.player.inventory.items):
        item_key = chr(ord("a") + i)
        item = list(self.engine.message_log.wrap(
          string=f"[{item_key}]-{item.name}",
          width=width-2
        ))
        lines += item + ['‎']
        height += len(item)
        
        # height += len(lines)
        if i > 0:
          height +=1
    else:
      lines = list(self.engine.message_log.wrap(
        string="Inventory is empty.",
        width=width-2
      ))
      height += len(lines)
    # adjust height based on number of lines
    height = min(4+height, self.engine.console.height)
    # set frame decoration based on height
    if height == self.engine.console.height:
      decoration = '┌─┐│ │└─┘'
    else:
      decoration = '┌─┐│ │├─┤'
    # draw inventory frame
    self.engine.console.draw_frame(
      x=x,
      y=y,
      width=width,
      height=height,
      clear=True,
      fg=(255, 255, 255),
      bg=(0, 0, 0),
      decoration=decoration
    )
    # draw inventory title
    self.engine.console.print(
      x=x+1,
      y=y,
      string=self.TITLE,
      bg=(255, 255, 255),
      fg=(0, 0, 0)
    )
    # draw pickup instruction
    self.engine.console.print(
      x=x+1,
      y=y+height-1,
      string='p-pick up',
    )
    # draw drop instruction
    string = 'd-drop'
    self.engine.console.print(
      x=self.engine.console.width - len(string)-1,
      y=y+height-1,
      string=string,
    )
    # print each line
    for line in lines:
      self.engine.console.print(
        x=x + 1, 
        y=1 + y + offset + 1, 
        string=line
      )
      offset += 1
      if offset > height:
        break

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
    player = self.engine.player
    key = event.sym
    index = key - tcod.event.KeySym.a

    if 0 <= index <= player.inventory.capacity:
      try:
        selected_item = player.inventory.items[index]
      except IndexError:
        self.engine.message_log.add_message(
          text="Invalid entry.", 
          fg=self.engine.colours['invalid']
        )
        return None
      return self.on_item_selected(item=selected_item)
    return super().ev_keydown(event=event)

  def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
    raise NotImplementedError()

class InventoryActivationHandler(InventoryEventHandler):

  def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
    return item.consumable.get_action(entity=self.engine.player)

class InventoryDropHandler(InventoryEventHandler):

  def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
    return action.DropItem(entity=self.engine.player, item=item)

class SelectIndexHandler(AskUserEventHandler):
  def __init__(self, engine: Engine):
    super().__init__(engine=engine)
    player = self.engine.player
    engine.mouse_location = (player.x, player.y)
  
  def on_render(self, console: tcod.console.Console = None) -> None:
    if console is None:
      console = self.engine.console
    super().on_render(console=console)
    x,y=self.engine.mouse_location
    self.engine.console.rgb['fg'][x,y]=self.engine.colours['black']
    self.engine.console.rgb['bg'][x,y]=self.engine.colours['white']
  
  def ev_keydown(self, event: tcod.event.KeyDown) ->  Optional[ActionOrHandler]:
    key = event.sym
    match key:
      case _:
        if key in MOVE_KEYS:
          # modify movement based on mod key
          mod = 1
          if event.mod & tcod.event.KMOD_SHIFT:
            mod *= 5
          if event.mod & tcod.event.KMOD_CTRL:
            mod *= 10
          if event.mod & tcod.event.KMOD_ALT:
            mod *= 20
          x,y = self.engine.mouse_location
          dx, dy = MOVE_KEYS[key]
          x+=dx*mod
          y+=dy*mod
          # clamp x and y to map size
          x=max(1, min(x, self.engine.game_map.width-2))
          y=max(1, min(y, self.engine.game_map.height-2))
          self.engine.mouse_location = x,y
          return None
        elif key in CONFIRM_KEYS:
          xy = self.engine.mouse_location
          return self.on_index_selected(*xy)
    return super().ev_keydown(event=event)

  def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
    raise NotImplementedError()

  def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
    return
  
  def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
    raise NotImplementedError()

class LookHandler(SelectIndexHandler):
  def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
    return MainGameEventHandler(engine=self.engine)

class MainGameEventHandler(EventHandler):
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
    performing_action: Optional[action.Action] = None
    player = self.engine.player
    # key = event.sym
    # if key in MOVE_KEYS:
    #   dx, dy = MOVE_KEYS[key]
    #   performing_action = action.BumpAction(entity=player, dx=dx, dy=dy)
    # elif key in WAIT_KEYS:
    #   performing_action = action.WaitAction(entity=player)
    # elif key == tcod.event.KeySym.ESCAPE:
    #   performing_action = action.EscapeAction(entity=self.engine.player)
    # elif key == tcod.event.KeySym.v:
    #   self.engine.event_handler = HistoryViewer(engine=self.engine)
    # elif key == tcod.event.KeySym.p:
    #   performing_action = action.PickupAction(entity=player)
    
    key = event.sym
    match key:
      case tcod.event.KeySym.ESCAPE:
        # performing_action = action.EscapeAction(entity=self.engine.player)
        raise SystemExit()
      case tcod.event.KeySym.v:
        return HistoryViewer(engine=self.engine)
      case tcod.event.KeySym.i:
        return InventoryActivationHandler(engine=self.engine)
      case tcod.event.KeySym.d:
        return InventoryDropHandler(engine=self.engine)
      case tcod.event.KeySym.x:
        return LookHandler(engine=self.engine)
      case tcod.event.KeySym.p:
        performing_action = action.PickupAction(entity=player)
      case _:
        if key in MOVE_KEYS:
          dx, dy = MOVE_KEYS[key]
          performing_action = action.BumpAction(entity=player, dx=dx, dy=dy)
        elif key in WAIT_KEYS:
          performing_action = action.WaitAction(entity=player)

    return performing_action

class GameOverEventHandler(EventHandler):
  def on_quit(self) -> None:
    """Handle exiting out of a finished game."""
    if os.path.exists(path="savegame.sav"):
      os.remove(path="savegame.sav")
    raise self.engine.exceptions.QuitWithoutSaving()

  def ev_quit(self, event: tcod.event.Quit) -> None:
    self.on_quit()
  def ev_keydown(self, event: tcod.event.KeyDown) -> None:
    if event.sym == tcod.event.KeySym.ESCAPE:
      # action.EscapeAction(entity=self.engine.player)
      self.on_quit()

class HistoryViewer(EventHandler):
  
  def __init__(self, engine:Engine):
    super().__init__(engine=engine)
    self.log_length = len(engine.message_log.messages)
    self.cursor = self.log_length - 1
  
  def on_render(self, console: tcod.console.Console = None) -> None:
    if console is None:
      console = self.engine.console
    super().on_render(console=console)

    log_console = tcod.console.Console(width=self.engine.console.width - 6, height=self.engine.console.height - 6)

    log_console.draw_frame(
      x=0,
      y=0,
      width=log_console.width, 
      height=log_console.height
    )
    log_console.print_box(
      x=0,
      y=0,
      width=log_console.width,
      height=1,
      string="┤Message history├",
      alignment=tcod.constants.CENTER
    )

    self.engine.message_log.render_messages(
      console=log_console,
      x=1,
      y=1,
      width=log_console.width - 2,
      height=log_console.height - 2,
      messages=self.engine.message_log.messages[: self.cursor +1],
    )

    log_console.blit(
      dest=self.engine.console,
      dest_x=3,
      dest_y=3,
    )
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
    # Fancy conditional movement to make it feel right.
    if event.sym in CURSOR_Y_KEYS:
      adjust = CURSOR_Y_KEYS[event.sym]
      if adjust < 0 and self.cursor == 0:
        # Only move from the top to the bottom when you're on the edge.
        self.cursor = self.log_length - 1
      elif adjust > 0 and self.cursor == self.log_length - 1:
        # Same with bottom to top movement.
        self.cursor = 0
      else:
        # Otherwise move while staying clamped to the bounds of the history log.
        self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
    elif event.sym == tcod.event.KeySym.HOME:
      self.cursor = 0  # Move directly to the top message.
    elif event.sym == tcod.event.KeySym.END:
      self.cursor = self.log_length - 1  # Move directly to the last message.
    else:  # Any other key moves back to the main game state.
      return MainGameEventHandler(engine=self.engine)
    return None

class SingleTargetSelectHandler(SelectIndexHandler):
  def __init__(
    self, 
    engine: Engine, 
    callback: Callable[[Tuple[int,int]], Optional[action.Action]]
  ):
    super().__init__(engine=engine)
    self.callback = callback
  def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:
    return self.callback((x,y))

class AreaRangedSelectHandler(SelectIndexHandler):
  def __init__(
    self, 
    engine: action.Engine,
    radius: int,
    callback: Callable[[Tuple[int,int]], Optional[action.Action]]
  ):
    super().__init__(engine=engine)
    self.radius = radius
    self.callback = callback
  def on_render(self, console: tcod.console.Console = None) -> None:
    if console is None:
      console = self.engine.console

    super().on_render(console=console)
    
    x,y = self.engine.mouse_location

    self.engine.console.draw_frame(
      x=x - self.radius - 1,
      y=y - self.radius - 1,
      width=self.radius ** 2,
      height=self.radius ** 2,
      fg=self.engine.colours['red'],
      clear=False
    )
  def on_index_selected(self, x: int, y: int) -> Optional[action.Action]:
    return self.callback((x,y))
