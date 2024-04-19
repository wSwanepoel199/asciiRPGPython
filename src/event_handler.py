from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod
import tcod.constants
import tcod.render
from src.actions import Action, EscapeAction, BumpAction, WaitAction

if TYPE_CHECKING:
  from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
  def __init__(self, engine: Engine) -> None:
    self.engine = engine

  def handle_events(self, context: tcod.context.Context) -> None:
    for event in tcod.event.wait():
      context.convert_event(event=event)
      self.dispatch(event=event)

  def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
    if self.engine.game_map.in_bounds(x=event.tile.x, y=event.tile.y):
      self.engine.mouse_location = event.tile.x, event.tile.y

  def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
    raise SystemExit()

  def on_render(self) -> None:
    self.engine.render()

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
  def handle_events(self, context: tcod.context.Context) -> None:
    for event in tcod.event.wait():
      context.convert_event(event=event)
      action = self.dispatch(event=event)

      if action is None:
        continue
      action.perform()
      self.engine.handle_enemy_turn()
      self.engine.update_fov()

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    action: Optional[Action] = None
    player = self.engine.player
    key = event.sym
    if key in MOVE_KEYS:
      dx, dy = MOVE_KEYS[key]
      action = BumpAction(entity=player, dx=dx, dy=dy)
    elif key in WAIT_KEYS:
      action = WaitAction(entity=player)
    elif key == tcod.event.KeySym.ESCAPE:
      action = EscapeAction(entity=self.engine.player)
    elif key == tcod.event.KeySym.v:
      self.engine.event_handler = HistoryViewer(engine=self.engine)

    return action

class GameOverEventHandler(EventHandler):
  def handle_events(self, context: tcod.context.Context) -> None:
    for event in tcod.event.wait():
      context.convert_event(event=event)
      action = self.dispatch(event=event)

      if action is None:
        continue

      action.perform()

  def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
    action: Optional[Action] = None

    key = event.sym

    if key == tcod.event.KeySym.ESCAPE:
      action = EscapeAction(entity=self.engine.player)
    # elif key == tcod.event.KeySym.SPACE:
    #   action = WaitAction(entity=self.engine.player)

    # No valid key was pressed
    return action
  
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

    log_console = tcod.console.Console(self.engine.console.width - 6, self.engine.console.height - 6)

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