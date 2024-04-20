from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod, traceback

import src.actions as action
# from src.actions import (
#   Action, 
#   EscapeAction, 
#   BumpAction, 
#   WaitAction,
#   PickupAction
# )

if TYPE_CHECKING:
  from src.engine import Engine
  from src.entity import Item

class EventHandler(tcod.event.EventDispatch[action.Action]):
  def __init__(self, engine: Engine) -> None:
    self.engine = engine

  def handle_events(self, context: tcod.context.Context) -> None:
    try:
      for event in tcod.event.wait():
        context.convert_event(event=event)
        # self.dispatch(event=event)
        self.handle_action(action=self.dispatch(event=event))
    except Exception: 
      traceback.print_exc()
      self.engine.message_log.add_message(
        text=traceback.format_exc(), 
        fg=self.engine.colours['error']
      )
  
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

  def ev_quit(self, event: tcod.event.Quit) -> Optional[action.Action]:
    raise SystemExit()

  def on_render(self) -> None:
    self.engine.render()

class AskUserEventHandler(EventHandler):
  def handle_action(self, action: Optional[action.Action]) -> bool:
    if super().handle_action(action=action):
      self.engine.event_handler = MainGameEventHandler(engine=self.engine)
      return True
    return False
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[action.Action]:
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
  
  def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[action.Action]:
    return self.on_exit()

  def on_exit(self) -> Optional[action.Action]:
    self.engine.event_handler = MainGameEventHandler(engine=self.engine)
    return None
  
class InventoryEventHandler(AskUserEventHandler):
  TITLE = " INVENTORY "

  def on_render(self) -> None:
    super().on_render()
    # ─│┌┐└├┤┬┴┼┘
    number_of_items_in_inventory = len(self.engine.player.inventory.items)
    height = number_of_items_in_inventory + 4

    if height == self.engine.console.height:
      decoration = '┌─┐│ │└─┘'
    else:
      decoration = '┌─┐│ │├─┤'
    x = self.engine.game_map.width
    y = 0
    width = self.engine.side_console
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


    if number_of_items_in_inventory > 0:
      for i, item in enumerate(self.engine.player.inventory.items):
        item_key = chr(ord("a") + i)
        self.engine.console.print(x=x + 1, y=y + i + 2, string=f"{item_key}-{item.name}")
    else:
      self.engine.console.print(x=x + 1, y=y + 2, string="(Empty)")

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[action.Action]:
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

  def on_item_selected(self, item: Item) -> Optional[action.Action]:
    raise NotImplementedError()

class InventoryActivationHandler(InventoryEventHandler):

  def on_item_selected(self, item: Item) -> Optional[action.Action]:
    return item.consumable.get_action(entity=self.engine.player)

class InventoryDropHandler(InventoryEventHandler):

  def on_item_selected(self, item: Item) -> Optional[action.Action]:
    return action.DropItem(entity=self.engine.player, item=item)

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

class MainGameEventHandler(EventHandler):

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[action.Action]:
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
        self.engine.event_handler = HistoryViewer(engine=self.engine)
      case tcod.event.KeySym.i:
        self.engine.event_handler = InventoryActivationHandler(engine=self.engine)
      case tcod.event.KeySym.p:
        performing_action = action.PickupAction(entity=player)
      case tcod.event.KeySym.d:
        self.engine.event_handler = InventoryDropHandler(engine=self.engine)
      case _:
        if key in MOVE_KEYS:
          dx, dy = MOVE_KEYS[key]
          performing_action = action.BumpAction(entity=player, dx=dx, dy=dy)
        elif key in WAIT_KEYS:
          performing_action = action.WaitAction(entity=player)

    return performing_action

class GameOverEventHandler(EventHandler):

  def ev_keydown(self, event: tcod.event.KeyDown) -> None:
    if event.sym == tcod.event.KeySym.ESCAPE:
      # action.EscapeAction(entity=self.engine.player)
      raise SystemExit()

CURSOR_Y_KEYS = {
  tcod.event.KeySym.UP: -1,
  tcod.event.KeySym.DOWN: 1,
  tcod.event.KeySym.PAGEUP: -10,
  tcod.event.KeySym.PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
  def __init__(self, engine:Engine):
    super().__init__(engine=engine)
    self.log_length = len(engine.message_log.messages)
    self.cursor = self.log_length - 1
  
  def on_render(self) -> None:
    super().on_render()

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
  
  def ev_keydown(self, event: tcod.event.KeyDown) -> None:
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
      self.engine.event_handler = MainGameEventHandler(engine=self.engine)